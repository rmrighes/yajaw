import asyncio
from functools import wraps

import httpx

import yajaw
from yajaw.core import exceptions, HttpStatusCode
from yajaw.utils import conversions

LOGGER = yajaw.CONFIG["log"]["logger"]
SEMAPHORE = yajaw.CONFIG["concurrency"]["semaphore"]
JIRA_PAT = yajaw.CONFIG["jira"]["token"]
JIRA_BASE_URL = yajaw.CONFIG["jira"]["base_url"]
SERVER_API = yajaw.CONFIG["jira"]["server_api_v2"]
AGILE_API = yajaw.CONFIG["jira"]["agile_api_v1"]
GREENHOPPER_API = yajaw.CONFIG["jira"]["greenhopper_api"]


# Classes for type hints


# class PaginationInfo(TypedDict):
#    startAt: int
#    maxResults: int
#    total: int


# class ClientInfo(TypedDict):
#    base_url: str
#    headers: dict[str]
#    params: dict[str]
#   auth: tuple[str]


# Custom authentication class for Personal Access Tokens


class PersonalAccessTokenAuth(httpx.Auth):
    def __init__(self, pat):
        self.token = pat

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


# Decorators


def retry(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        attempt = 1
        tries = 10
        delay = 0.1
        backoff = 1.8
        while attempt <= tries:
            try:
                result: httpx.Response = await func(*args, **kwargs)
                if isinstance(result, httpx.Response):
                    if result.status_code == httpx.codes.OK:
                        LOGGER.debug(
                            f"status code {result.status_code} -- attemp {attempt:02d}"
                        )
                        return result
                    LOGGER.debug(
                        f"status code {result.status_code} -- "
                        f"attemp {attempt:02d} -- sleeping for {delay:.2f} seconds"
                    )
            except httpx.ConnectError:
                LOGGER.debug(f"No valid response received -- attemp {attempt:02d}")
            finally:
                await asyncio.sleep(delay)
                attempt += 1
                delay *= backoff
        LOGGER.error("Unable to complete the request successfully.")
        # return result

    return wrapper


def generate_headers() -> dict[str]:
    return {"Accept": "application/json", "Content-Type": "application/json"}


def generate_params(
    new_params: dict[str], existing_params: dict[str] = None
) -> dict[str]:
    if existing_params is None:
        existing_params = {}
    return existing_params | new_params


def generate_payload(
    new_content: dict[str], existing_content: dict[str] = None
) -> dict[str]:
    if existing_content is None:
        existing_content = {}
    return existing_content | new_content


def generate_auth() -> PersonalAccessTokenAuth:
    return PersonalAccessTokenAuth(JIRA_PAT)


def generate_url(resource: str) -> str:
    return f"{JIRA_BASE_URL}/{SERVER_API}/{resource}"


def generate_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        auth=generate_auth(), headers=generate_headers(), timeout=None
    )


def is_valid_response(response: httpx.Response) -> bool:
    return response.status_code == httpx.codes.OK


def is_resource_unauthorized(response: httpx.Response) -> bool:
    return response.status_code == HttpStatusCode.UNAUTHORIZED


def is_resource_forbideen(response: httpx.Response) -> bool:
    return response.status_code == HttpStatusCode.FORBIDDEN


def is_resource_not_found(response: httpx.Response) -> bool:
    return response.status_code == HttpStatusCode.NOT_FOUND


@retry
async def send_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    params: dict[str] = None,
    payload: dict[str] = None,
) -> httpx.Response:
    response = await client.request(method=method, url=url, params=params, json=payload)
    if is_valid_response(response):
        return response
    if is_resource_unauthorized(response):
        raise exceptions.ResourceUnauthorizedError
    if is_resource_forbideen(response):
        raise exceptions.ResourceForbiddenError
    if is_resource_not_found(response):
        raise exceptions.ResourceNotFoundError
    return None


async def send_single_request(
    method: str, resource: str, params: dict[str] = None, payload: dict[str] = None
) -> list[httpx.Response]:
    responses = []
    try:
        client = generate_client()
        url = generate_url(resource=resource)
        async with client, SEMAPHORE:
            task = asyncio.create_task(
                send_request(
                    client=client,
                    method=method,
                    url=url,
                    params=params,
                    payload=payload,
                )
            )
            response = await task
        LOGGER.info(
            f"{response.status_code} -- {response.request.method} {response.request.url}"
        )
        if payload is not None:
            LOGGER.info(f"{payload}")
        responses.append(response)
    except exceptions.ResourceUnauthorizedError as e:
        raise exceptions.ResourceUnauthorizedError from e
    except exceptions.ResourceForbiddenError as e:
        raise exceptions.ResourceForbiddenError from e
    except exceptions.ResourceNotFoundError as e:
        raise exceptions.ResourceNotFoundError from e
    return responses


# 1. Send a single request and get the response
# 2. Evaluate if there are additional pages to be retrieved
# 3. Return the list of requests if there are no additional pages
# 4. Determine the list of pages to be requested
# 5. Generate a list of attributes for additional requests
# 6. Concurrently send the requests based on the list of attributes
# 7. Update the list of responses and return it


async def send_paginated_requests(
    method: str, resource: str, params: dict[str] = None, payload: dict[str] = None
) -> list[httpx.Response]:
    default_pagination = [{"startAt": 0, "maxResults": 10}]

    attributes_list = generate_paginated_attributes_list(
        pagination_list=default_pagination,
        method=method,
        resource=resource,
        params=params,
        payload=payload,
    )

    responses = await send_single_request(
        method=attributes_list[0]["method"],
        resource=attributes_list[0]["resource"],
        params=attributes_list[0]["params"],
        payload=attributes_list[0]["payload"],
    )

    initial_response = conversions.process_single_nonpaginated_resource(responses)

    paginated_attributes = fetch_paginated_attributes(initial_response)

    if is_pagination_required(paginated_attributes):
        pagination_list = generate_pages_list(paginated_attributes)

        attributes_list = generate_paginated_attributes_list(
            pagination_list=pagination_list,
            method=method,
            resource=resource,
            params=params,
            payload=payload,
        )

        client = generate_client()
        async with client, SEMAPHORE:
            tasks = [
                asyncio.create_task(
                    send_single_request(
                        method=attributes["method"],
                        resource=attributes["resource"],
                        params=attributes["params"],
                        payload=attributes["payload"],
                    )
                )
                for attributes in attributes_list
            ]
            paginated_responses = await asyncio.gather(*tasks)
        for response in paginated_responses:
            responses.extend(response)

    return responses


def fetch_paginated_attributes(response: httpx.Response) -> dict:
    paginated_attributes = {}
    paginated_attributes["start_at"] = (
        response["startAt"] if "startAt" in response else None
    )
    paginated_attributes["max_results"] = (
        response["maxResults"] if "maxResults" in response else None
    )
    paginated_attributes["total"] = response["total"] if "total" in response else None
    return paginated_attributes


def is_pagination_required(paginated_attributes: dict) -> bool:
    start_at = paginated_attributes["start_at"]
    max_results = paginated_attributes["max_results"]
    total = paginated_attributes["total"]
    return start_at + max_results < total


def generate_pages_list(paginated_attributes: dict) -> list[dict]:
    paginated_attributes["start_at"] = paginated_attributes["max_results"]
    page_list = [
        paginated_attributes["start_at"] + i * paginated_attributes["max_results"]
        for i in range(
            int(paginated_attributes["total"] / paginated_attributes["max_results"])
        )
    ]
    pagination_list = [
        {"startAt": page, "maxResults": paginated_attributes["max_results"]}
        for page in page_list
    ]
    return pagination_list


def generate_paginated_attributes_list(
    pagination_list: list[dict],
    method: str,
    resource: str,
    params: dict[str],
    payload: dict[str],
) -> list[dict]:
    attributes_list = []
    for pagination in pagination_list:
        attributes = {}
        attributes["method"] = method
        attributes["resource"] = resource
        attributes["params"] = params
        attributes["payload"] = payload
        if method == "GET":
            attributes["params"] = generate_params(
                new_params=pagination, existing_params=params
            )
        elif method == "POST":
            attributes["payload"] = generate_payload(
                new_content=pagination, existing_content=payload
            )
        attributes_list.append(attributes)
    return attributes_list
