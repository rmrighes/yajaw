"""Module responsible for lower level HTTP requests."""
import asyncio
import math
from functools import wraps
from http import HTTPStatus
from random import uniform

import httpx

import yajaw
from yajaw.core import exceptions


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


def generate_params(new_params: dict[str], existing_params: dict[str] | None = None) -> dict[str]:
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


def generate_url(resource: str, api: str) -> str:
    """Function responsible for generating the url info for HTTP requests."""
    return f"{yajaw.JIRA_BASE_URL}/{api}/{resource}"


def generate_auth() -> PersonalAccessTokenAuth:
    """Function responsible for generating the authentication info for HTTP requests."""
    return PersonalAccessTokenAuth(yajaw.JIRA_PAT)


def generate_client() -> httpx.AsyncClient:
    """Function responsible for generating the client used in the context for HTTP requests."""
    return httpx.AsyncClient(
        auth=generate_auth(),
        headers=generate_headers(),
        timeout=yajaw.TIMEOUT,
        follow_redirects=True,
    )


class JiraInfo:
    """TBD"""

    def __init__(
        self,
        info: dict,
    ):
        self.__method = info["method"]
        self.__resource = info["resource"]
        self.__api = info["api"]
        self.__url = generate_url(resource=info["resource"], api=info["api"])
        self.__params = info["params"]
        self.__payload = info["payload"]

    @property
    def method(self):
        """TBD"""
        return self.__method

    @method.setter
    def method(self, mhd: str):
        """TBD"""
        self.__method = mhd

    @property
    def resource(self):
        """TBD"""
        return self.__resource

    @resource.setter
    def resource(self, rce: str):
        """TBD"""
        self.__resource = rce

    @property
    def api(self):
        """TBD"""
        return self.__api

    @api.setter
    def api(self, api: str):
        """TBD"""
        self.__api = api

    @property
    def url(self):
        """TBD"""
        return self.__url

    @url.setter
    def url(self, url: str):
        """TBD"""
        self.__url = url

    @property
    def params(self):
        """TBD"""
        return self.__params

    @params.setter
    def params(self, pms: dict):
        """TBD"""
        self.__params = pms

    @property
    def payload(self):
        """TBD"""
        return self.__payload

    @payload.setter
    def payload(self, pad: dict):
        """TBD"""
        self.__payload = pad


def retry_response_error_detected(result: httpx.Response) -> bool:
    """TBD"""
    proceed: bool = True

    if not isinstance(result, httpx.Response):
        yajaw.LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.InvalidResponseError
    if result.status_code == HTTPStatus.UNAUTHORIZED:
        yajaw.LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceUnauthorizedError
    if result.status_code == HTTPStatus.FORBIDDEN:
        yajaw.LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceForbiddenError
    if result.status_code == HTTPStatus.NOT_FOUND:
        yajaw.LOGGER.warning("AAApending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceNotFoundError
    if result.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        yajaw.LOGGER.error("pending log message -- no_retry_response_error_detected")
        raise exceptions.ResourceMethodNotAllowedError
    if httpx.codes.is_success(result.status_code):
        proceed = False
    return proceed


def retry(func):
    """TBD"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        attempt = 1
        delay = uniform(0, yajaw.DELAY)
        while attempt <= yajaw.TRIES:
            await asyncio.sleep(delay)
            result: httpx.Response = await func(*args, **kwargs)
            if not retry_response_error_detected(result):
                yajaw.LOGGER.info(
                    f"{result.status_code} - attempt {attempt:02d} - "
                    f"delay {delay:04.2f}s -- {result.request.method} "
                    f"{result.request.url}"
                )
                return result
            yajaw.LOGGER.info(
                f"{result.status_code} - attempt {attempt:02d} - "
                f"delay {delay:04.2f}s -- {result.request.method} "
                f"{result.request.url}"
            )
            attempt += 1
            delay *= yajaw.BACKOFF
        yajaw.LOGGER.error(
            f"{result.status_code} - attempt {attempt:02d} - "
            f"delay {delay:04.2f}s -- {result.request.method} "
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
    async with yajaw.SEMAPHORE:
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
        yajaw.LOGGER.warning("pending log message -- send_single_request")
        raise exceptions.ResourceNotFoundError from exc
    except exceptions.YajawError as e:
        yajaw.LOGGER.exception("pending log message -- send_single_request")
        raise exceptions.YajawError from e
    return response


async def send_paginated_requests(jira: JiraInfo) -> list[httpx.Response]:
    """Function that wraps send_single_request and and call it for all necessary pages."""
    default_page_attr = yajaw.DEFAULT_PAGINATION
    jira_list = create_jira_list_with_page_attr(page_attr_list=[default_page_attr], jira=jira)
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
            jira_list = create_jira_list_with_page_attr(page_attr_list=page_attr_list, jira=jira)

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
        for i in range(int(math.ceil(page_attr["total"] / page_attr["max_results"])) - 1)
    ]
    return [{"startAt": page, "maxResults": page_attr["max_results"]} for page in page_attr_list]


def create_jira_list_with_page_attr(page_attr_list: list[dict], jira: JiraInfo) -> list[JiraInfo]:
    """Function that gets a list of page attributes and createa
    a list with respective JiraInfo objects."""
    jira_list = []
    for page_attr in page_attr_list:
        unique_info = {
            "method": jira.method,
            "resource": jira.resource,
            "api": jira.api,
            "params": jira.params,
            "payload": jira.payload,
        }
        if unique_info["method"] == "GET":
            unique_info["params"] = generate_params(
                new_params=page_attr, existing_params=unique_info["params"]
            )
        if unique_info["method"] == "POST":
            unique_info["payload"] = generate_payload(
                new_content=page_attr, existing_content=unique_info["payload"]
            )
        unique_jira = JiraInfo(info=unique_info)
        jira_list.append(unique_jira)
    return jira_list


def retrieve_pagination_attributes(response: httpx.Response) -> dict:
    """TBD"""
    page_attr = {}
    response_json = response.json()
    page_attr["start_at"] = response_json["startAt"] if "startAt" in response_json else None
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
