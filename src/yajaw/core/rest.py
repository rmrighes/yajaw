import asyncio
import httpx
from typing import TypedDict
from yajaw import settings
from yajaw.utils import conversions


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
    return {
        "Accept": "application/json",
    }


def generate_params() -> dict[str]:
    ...


def generate_auth() -> PersonalAccessTokenAuth:
    return PersonalAccessTokenAuth(settings.JIRA_PAT)


def generate_url(resource: str) -> str:
    return f"{settings.JIRA_BASE_URL}/{settings.JIRA_API_V2}/{resource}"


def generate_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(auth=generate_auth(), headers=generate_headers())


async def send_request(
    client: httpx.AsyncClient, method: str, url: str
) -> httpx.Response:
    return await client.request(method=method, url=url)


def generate_pagination(response: httpx.Response) -> PaginationInfo | None:
    ...


"""
Controls concurrency and paginated requests for a single resource 
"""


async def send_paginated_request(method: str, resource: str) -> list[httpx.Response]:
    responses = list()
    client = generate_client()
    url = generate_url(resource=resource)
    async with client:
        task = asyncio.create_task(send_request(client=client, method=method, url=url))
        response = await task
    responses.append(response)
    converted_responses = conversions.generate_list_of_responses(responses)
    return converted_responses
