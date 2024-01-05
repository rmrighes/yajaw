import asyncio
import httpx
from typing import TypedDict
from yajaw import settings

# Classes for type hints


class PaginationInfo(TypedDict):
    startAt: int
    maxResults: int
    total: int


class ClientInfo(TypedDict):
    base_url: str
    headers: dict[str]
    params: dict[str]
    auth: tuple[str]


"""
Custom authentication class for Personal Access Tokens
"""


class PersonalAccessTokenAuth(httpx.Auth):
    def __init__(self, token):
        self.token = settings.JIRA_PAT

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def generate_headers() -> dict[str]:
    return {"Accept": "application/json", "Content-Type": "application/json"}


def generate_params(
    new_params: dict[str], existing_params: dict[str] = dict()
) -> dict[str]:
    return existing_params | new_params


def generate_payload(
    new_content: dict[str], existing_content: dict[str] = dict()
) -> dict[str]:
    return existing_content | new_content


def generate_auth() -> PersonalAccessTokenAuth:
    return PersonalAccessTokenAuth(settings.JIRA_PAT)


def generate_url(resource: str) -> str:
    return f"{settings.JIRA_BASE_URL}/{settings.JIRA_API_V2}/{resource}"


def generate_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        auth=generate_auth(), headers=generate_headers(), timeout=None
    )


async def send_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    params: dict[str] = None,
    payload: dict[str] = None,
) -> httpx.Response:
    return await client.request(method=method, url=url, params=params, json=payload)


"""
Controls concurrency and paginated requests for a single resource 
"""


async def send_single_request(
    method: str, resource: str, payload: dict[str] = None
) -> list[httpx.Response]:
    responses = list()
    client = generate_client()
    url = generate_url(resource=resource)
    async with client:
        task = asyncio.create_task(
            send_request(client=client, method=method, url=url, payload=payload)
        )
        response = await task
    responses.append(response)
    return responses


async def send_paginated_requests(
    method: str, resource: str, params: dict[str] = None, payload: dict[str] = None
) -> list[httpx.Response]:
    responses = list()
    pagination = {"startAt": 0, "maxResults": 50}
    if method == "GET":
        params = generate_params(new_params=pagination)
    elif method == "POST":
        payload = generate_payload(new_content=pagination, existing_content=payload)
    client = generate_client()
    url = generate_url(resource=resource)
    async with client:
        task = asyncio.create_task(
            send_request(
                client=client, method=method, url=url, params=params, payload=payload
            )
        )
        response = await task
    responses.append(response)

    # Check result for multiple pages
    initial_response = responses[0].json()
    start_at = initial_response["startAt"] if "startAt" in initial_response else None
    max_results = (
        initial_response["maxResults"] if "maxResults" in initial_response else None
    )
    total = initial_response["total"] if "total" in initial_response else None

    if start_at + max_results < total:
        start_at = max_results
        page_list = [
            start_at + i * max_results for i in range(int(total / max_results))
        ]
        pagination_list = [
            {"startAt": page, "maxResults": max_results} for page in page_list
        ]

        attributes_list = list()
        for pagination in pagination_list:
            attributes = dict()
            attributes["method"] = method
            attributes["url"] = url
            attributes["params"] = params
            attributes["payload"] = payload
            if method == "GET":
                attributes["params"] = generate_params(new_params=pagination)
            elif method == "POST":
                attributes["payload"] = generate_payload(
                    new_content=pagination, existing_content=payload
                )
            attributes_list.append(attributes)
        client = generate_client()
        async with client:
            tasks = [
                asyncio.create_task(
                    send_request(
                        client=client,
                        method=attributes["method"],
                        url=attributes["url"],
                        params=attributes["params"],
                        payload=attributes["payload"],
                    )
                )
                for attributes in attributes_list
            ]
            paginated_responses = await asyncio.gather(*tasks)
    responses.extend(paginated_responses)
    return responses
