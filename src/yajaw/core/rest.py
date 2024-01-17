"""Module responsible for lower level HTTP requests."""
import asyncio
import math
import secrets
from http import HTTPStatus

import httpx

from yajaw import Option, YajawConfig
from yajaw.core import exceptions


class PersonalAccessTokenAuth(httpx.Auth):
    """Class used for Personal Access Token auth in httpx."""

    def __init__(self, pat):
        self.token = pat

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def _generate_headers() -> dict:
    """Function responsible for generating the headers info for HTTP requests."""
    return {"Accept": "application/json", "Content-Type": "application/json"}


def _generate_params(new_params: dict, existing_params: dict | None = None) -> dict:
    """Function responsible for generating the parameters info for HTTP requests."""
    if existing_params is None:
        existing_params = {}
    return existing_params | new_params


def _generate_payload(new_content: dict, existing_content: dict | None = None) -> dict:
    """Function responsible for generating the payload info for HTTP requests."""
    if existing_content is None:
        existing_content = {}
    return existing_content | new_content


def _generate_url(resource: str, api: str) -> str:
    """Function responsible for generating the url info for HTTP requests."""
    return f"{YajawConfig.JIRA_BASE_URL}/{api}/{resource}"


def _generate_auth() -> PersonalAccessTokenAuth:
    """Function responsible for generating the authentication info for HTTP requests."""
    return PersonalAccessTokenAuth(YajawConfig.JIRA_PAT)


def _generate_client() -> httpx.AsyncClient:
    """Function responsible for generating the client used in the context for HTTP requests."""
    return httpx.AsyncClient(
        auth=_generate_auth(),
        headers=_generate_headers(),
        timeout=YajawConfig.TIMEOUT,
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
        self.__url = _generate_url(resource=info["resource"], api=info["api"])
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


def _retry_response_error_detected(result: httpx.Response) -> bool:
    """Check if a retry should proceed based on the HTTP response."""
    retry = True
    if not isinstance(result, httpx.Response):
        _log_and_raise_request_issue("InvalidResponseError")
    if result.status_code == HTTPStatus.UNAUTHORIZED:
        _log_and_raise_request_issue("ResourceUnauthorizedError")
    if result.status_code == HTTPStatus.FORBIDDEN:
        _log_and_raise_request_issue("ResourceForbiddenError")
    if result.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        _log_and_raise_request_issue("ResourceMethodNotAllowedError")
    if result.status_code == HTTPStatus.NOT_FOUND:
        _log_and_raise_request_issue("ResourceNotFoundError")
    if httpx.codes.is_success(result.status_code):
        retry = False
    return retry


def _log_and_raise_request_issue(error_type: str, warning: Option = Option.NO) -> None:
    """Log an error or warning message and raise the specified exception."""
    log_level = YajawConfig.LOGGER.warning if warning is Option.YES else YajawConfig.LOGGER.error
    log_message = f"log message -- {error_type}"
    log_level(log_message)
    raise getattr(exceptions, error_type)


async def _retry_request(jira: JiraInfo, client: httpx.AsyncClient):
    """Retry the given function on certain conditions."""
    delay = secrets.SystemRandom().uniform(0, YajawConfig.DELAY)
    for attempt in range(1, YajawConfig.TRIES + 1):
        await asyncio.sleep(delay)
        result = await _send_request(jira=jira, client=client)
        _log_attempt_info(result, attempt, delay, error=Option.NO)
        if not _retry_response_error_detected(result):
            return result
        delay *= YajawConfig.BACKOFF
    _log_attempt_info(result, attempt, delay, error=Option.YES)
    raise exceptions.InvalidResponseError


def _log_attempt_info(result, attempt, delay, error=Option.NO):
    """Log information for a retry attempt."""
    log_level = YajawConfig.LOGGER.error if error == Option.YES else YajawConfig.LOGGER.info

    if isinstance(result, httpx.Response):
        log_message = (
            f"{result.status_code} - attempt {attempt:02d} - "
            f"delay {delay:05.2f}s -- {result.request.method} "
            f"{result.request.url}"
        )
    else:
        log_message = f"Non-HTTPX response - attempt {attempt:02d} - delay {delay:04.2f}s"

    log_level(log_message)


async def _send_request(jira: JiraInfo, client: httpx.AsyncClient) -> httpx.Response:
    """Function responsible for making a low-level HTTP request."""
    method, url, params, payload = jira.method, jira.url, jira.params, jira.payload
    async with YajawConfig.SEMAPHORE:
        return await client.request(method=method, url=url, params=params, json=payload)


async def send_single_request(
    jira: JiraInfo, client: httpx.AsyncClient | None = None
) -> httpx.Response:
    """Function wraps retry_request and returns a list of responses."""
    try:
        if client is None:
            client = _generate_client()
        task = asyncio.create_task(_retry_request(jira=jira, client=client))
        response = await task
    except exceptions.ResourceNotFoundError as exc:
        YajawConfig.LOGGER.warning("pending log message -- send_single_request")
        raise exceptions.ResourceNotFoundError from exc
    except exceptions.YajawError as e:
        YajawConfig.LOGGER.exception("pending log message -- send_single_request")
        raise exceptions.YajawError from e
    return response


async def send_paginated_requests(jira: JiraInfo) -> list[httpx.Response]:
    """Function that wraps send_single_request and and call it for all necessary pages."""
    default_page_attr = YajawConfig.DEFAULT_PAGINATION
    jira_list = _create_jira_list_with_page_attr(page_attr_list=[default_page_attr], jira=jira)
    initial_jira = jira_list[0]

    client = _generate_client()
    async with client:
        # First request with default pagination
        response = await send_single_request(jira=initial_jira, client=client)

        responses = []
        responses.append(response)

        # Identify if additional requests are needed
        page_attr = _retrieve_pagination_attributes(response=response)
        if _is_pagination_required(page_attr=page_attr):
            # Generate the updated page_attr_list
            page_attr_list = _create_list_of_page_attr(page_attr=page_attr)

            # Generate the updated jira_list
            jira_list = _create_jira_list_with_page_attr(page_attr_list=page_attr_list, jira=jira)

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


def _create_list_of_page_attr(page_attr: dict) -> list[dict]:
    """Function that generates a list of attributes needed to retrieve all pages."""
    if "total" not in page_attr:
        return [page_attr]

    page_attr["start_at"] = page_attr["max_results"]

    page_attr_list = [
        page_attr["start_at"] + i * page_attr["max_results"]
        for i in range(int(math.ceil(page_attr["total"] / page_attr["max_results"])) - 1)
    ]
    return [{"startAt": page, "maxResults": page_attr["max_results"]} for page in page_attr_list]


def _create_jira_list_with_page_attr(page_attr_list: list[dict], jira: JiraInfo) -> list[JiraInfo]:
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
            unique_info["params"] = _generate_params(
                new_params=page_attr, existing_params=unique_info["params"]
            )
        if unique_info["method"] == "POST":
            unique_info["payload"] = _generate_payload(
                new_content=page_attr, existing_content=unique_info["payload"]
            )
        unique_jira = JiraInfo(info=unique_info)
        jira_list.append(unique_jira)
    return jira_list


def _retrieve_pagination_attributes(response: httpx.Response) -> dict:
    """TBD"""
    page_attr = {}
    response_json = response.json()
    page_attr["start_at"] = response_json["startAt"] if "startAt" in response_json else None
    page_attr["max_results"] = (
        response_json["maxResults"] if "maxResults" in response_json else None
    )
    page_attr["total"] = response_json["total"] if "total" in response_json else None
    return page_attr


def _is_pagination_required(page_attr: dict) -> bool:
    """Function that checks if pagination is required."""
    start_at = page_attr["start_at"]
    max_results = page_attr["max_results"]
    total = page_attr["total"]
    return start_at + max_results < total
