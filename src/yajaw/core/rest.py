"""Module responsible for lower level HTTP requests."""
import asyncio
import math
from functools import wraps
from http import HTTPStatus

import httpx

import yajaw
from yajaw.core import exceptions

# Module Constants
TRIES = yajaw.CONFIG["retries"]["tries"]
DELAY = yajaw.CONFIG["retries"]["delay"]
BACKOFF = yajaw.CONFIG["retries"]["backoff"]
YAJAW_LOGGER = yajaw.CONFIG["log"]["logger"]
SEMAPHORE = yajaw.CONFIG["concurrency"]["semaphore"]
JIRA_PAT = yajaw.CONFIG["jira"]["token"]
JIRA_BASE_URL = yajaw.CONFIG["jira"]["base_url"]
SERVER_API = yajaw.CONFIG["jira"]["server_api_v2"]
AGILE_API = yajaw.CONFIG["jira"]["agile_api_v1"]
GREENHOPPER_API = yajaw.CONFIG["jira"]["greenhopper_api"]
DEFAULT_PAGINATION = yajaw.CONFIG["pagination"]["default"]
TIMEOUT = yajaw.CONFIG["requests"]["timeout"]


class PersonalAccessTokenAuth(httpx.Auth):
    """Class used for Personal Access Token auth in httpx."""

    def __init__(self, pat):
        self.token = pat

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def generate_headers() -> dict[str]:
    """Function responsible for generating the headers info for HTTP requests."""
    return {"Accept": "application/json", "Content-Type": "application/json"}


def generate_params(
    new_params: dict[str], existing_params: dict[str] | None = None
) -> dict[str]:
    """Function responsible for generating the parameters info for HTTP requests."""
    if existing_params is None:
        existing_params = {}
    return existing_params | new_params


def generate_payload(
    new_content: dict[str], existing_content: dict[str] | None = None
) -> dict[str]:
    """Function responsible for generating the payload info for HTTP requests."""
    if existing_content is None:
        existing_content = {}
    return existing_content | new_content


def generate_url(resource: str) -> str:
    """Function responsible for generating the url info for HTTP requests."""
    return f"{JIRA_BASE_URL}/{SERVER_API}/{resource}"


def generate_auth() -> PersonalAccessTokenAuth:
    """Function responsible for generating the authentication info for HTTP requests."""
    return PersonalAccessTokenAuth(JIRA_PAT)


def generate_client() -> httpx.AsyncClient:
    """Function responsible for generating the client used in the context for HTTP requests."""
    return httpx.AsyncClient(
        auth=generate_auth(),
        headers=generate_headers(),
        timeout=TIMEOUT,
        follow_redirects=True,
    )


class JiraInfo:
    def __init__(
        self,
        method: str,
        resource: str,
        params: dict | None = None,
        payload: dict | None = None,
    ):
        self._method = method
        self._resource = resource
        self._url = generate_url(resource=resource)
        self._params = params
        self._payload = payload

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, mhd: str):
        self._method = mhd

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, rce: str):
        self._resource = rce

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url: str):
        self._url = url

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, pms: dict):
        self._params = pms

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, pad: dict):
        self._payload = pad


def retry_response_error_detected(result: httpx.Response) -> bool:
    proceed: bool = True

    if not isinstance(result, httpx.Response):
        YAJAW_LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.InvalidResponseError
    if result.status_code == HTTPStatus.UNAUTHORIZED:
        YAJAW_LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceUnauthorizedError
    if result.status_code == HTTPStatus.FORBIDDEN:
        YAJAW_LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceForbiddenError
    if result.status_code == HTTPStatus.NOT_FOUND:
        YAJAW_LOGGER.warning("AAApending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceNotFoundError
    if result.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        YAJAW_LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceMethodNotAllowedError
    if httpx.codes.is_success(result.status_code):
        proceed = False
    return proceed


def retry(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        attempt = 1
        delay = DELAY
        while attempt <= TRIES:
            result: httpx.Response = await func(*args, **kwargs)
            if not retry_response_error_detected(result):
                YAJAW_LOGGER.info(
                    f"{result.status_code} - attempt {attempt:02d} - "
                    f"delay {delay:05.2f}s -- {result.request.method} "
                    f"{result.request.url}"
                )
                return result
            YAJAW_LOGGER.info(
                f"{result.status_code} - attempt {attempt:02d} - "
                f"delay {delay:05.2f}s -- {result.request.method} "
                f"{result.request.url}"
            )
            await asyncio.sleep(delay)
            attempt += 1
            delay *= BACKOFF
        YAJAW_LOGGER.error(
            f"{result.status_code} - attempt {attempt:02d} - "
            f"delay {delay:05.2f}s -- {result.request.method} "
            f"{result.request.url}"
        )
        raise exceptions.InvalidResponseError

    return wrapper


@retry
async def send_request(jira: JiraInfo, client: httpx.AsyncClient) -> httpx.Response:
    """Function responsible for making a low level HTTP request."""
    method = jira.method
    url = jira.url
    params = jira.params
    payload = jira.payload
    async with SEMAPHORE:
        return await client.request(method=method, url=url, params=params, json=payload)


async def send_single_request(
    jira: JiraInfo, client: httpx.AsyncClient | None = None
) -> httpx.Response:
    """Function wraps send_request and returns a list of responses."""
    try:
        if client is None:
            client = generate_client()
        task = asyncio.create_task(send_request(jira=jira, client=client))
        response = await task
    except exceptions.ResourceNotFoundError as exc:
        YAJAW_LOGGER.warning("pending log message -- send_single_request")
        raise exceptions.ResourceNotFoundError from exc
    except exceptions.YajawError as e:
        YAJAW_LOGGER.exception("pending log message -- send_single_request")
        raise exceptions.YajawError from e
    return response


async def send_paginated_requests(jira: JiraInfo) -> list[httpx.Response]:
    """Function that wraps send_single_request and and call it for all necessary pages."""
    default_page_attr = DEFAULT_PAGINATION
    jira_list = create_jira_list_with_page_attr(
        page_attr_list=[default_page_attr], jira=jira
    )
    initial_jira = jira_list[0]

    client = generate_client()
    async with client:
        # First request with default pagination
        response = await send_single_request(jira=initial_jira, client=client)

        responses = []
        responses.append(response)

        # Identify if additional requests are needed
        page_attr = retrieve_pagination_attributes(response=response)
        if is_pagination_required(page_attr=page_attr):
            # Generate the updated page_attr_list
            page_attr_list = create_list_of_page_attr(page_attr=page_attr)

            # Generate the updated jira_list
            jira_list = create_jira_list_with_page_attr(
                page_attr_list=page_attr_list, jira=jira
            )

            # Create concurrent requests for the additional pages
            # iterate over jira_list
            # Consolidate responses list
            # for response in paginated_responses: responses.extend(response)

            tasks = [
                asyncio.create_task(send_single_request(jira=jira, client=client))
                for jira in jira_list
            ]
            group_of_response = await asyncio.gather(*tasks)

            responses.extend(list(group_of_response))


    return responses


def create_list_of_page_attr(page_attr: dict) -> list[dict]:
    """Function that generates a list of attributes needed to retrieve all pages."""
    if "total" not in page_attr:
        return [page_attr]

    page_attr["start_at"] = page_attr["max_results"]

    page_attr_list = [
        page_attr["start_at"] + i * page_attr["max_results"]
        for i in range(
            int(math.ceil(page_attr["total"] / page_attr["max_results"])) - 1
        )
    ]
    return [
        {"startAt": page, "maxResults": page_attr["max_results"]}
        for page in page_attr_list
    ]


def create_jira_list_with_page_attr(
    page_attr_list: list[dict], jira: JiraInfo
) -> list[JiraInfo]:
    """Function that gets a list of page attributes and createa
    a list with respective JiraInfo objects."""
    jira_list = []
    for page_attr in page_attr_list:
        unique_jira = JiraInfo(
            method=jira.method,
            resource=jira.resource,
            params=jira.params,
            payload=jira.payload,
        )
        if unique_jira.method == "GET":
            unique_jira.params = generate_params(
                new_params=page_attr, existing_params=unique_jira.params
            )
        if unique_jira.method == "POST":
            unique_jira.payload = generate_payload(
                new_content=page_attr, existing_content=unique_jira.payload
            )
        jira_list.append(unique_jira)
    return jira_list


def retrieve_pagination_attributes(response: httpx.Response) -> dict:
    page_attr = {}
    response_json = response.json()
    page_attr["start_at"] = (
        response_json["startAt"] if "startAt" in response_json else None
    )
    page_attr["max_results"] = (
        response_json["maxResults"] if "maxResults" in response_json else None
    )
    page_attr["total"] = response_json["total"] if "total" in response_json else None
    return page_attr


def is_pagination_required(page_attr: dict) -> bool:
    """Function that checks if pagination is required."""
    start_at = page_attr["start_at"]
    max_results = page_attr["max_results"]
    total = page_attr["total"]
    return start_at + max_results < total
