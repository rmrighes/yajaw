""" Module responsible for the externally accessible functions wrapping
the Jira API."""
import asyncio

from yajaw.core import exceptions, rest
from yajaw.utils import conversions

type ListResponses = list[dict[any]]
type SingleResponse = dict[any]


async def async_fetch_all_projects(expand: dict | None = None) -> ListResponses:
    """Wrapper async function for GET /project"""
    method = "GET"
    resource = "project"
    if expand is None:
        expand = {}
    try:
        response = await rest.send_single_request(method=method, resource=resource, params=expand)
        return conversions.process_multiple_nonpaginated_resources(responses=response)
    except exceptions.InvalidResponseError:
        return []


def fetch_all_projects(expand: dict | None = None) -> ListResponses:
    """Wrapper sync function for GET /project"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_all_projects(expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_project(project_key: str, expand: dict | None = None) -> SingleResponse:
    """Wrapper async function for GET /project/{key}"""
    method = "GET"
    resource = f"project/{project_key}"
    if expand is None:
        expand = {}
    try:
        response = await rest.send_single_request(method=method, resource=resource, params=expand)
        return conversions.process_single_nonpaginated_resource(responses=response)
    except exceptions.InvalidResponseError:
        return {}


def fetch_project(project_key: str, expand: dict | None = None) -> SingleResponse:
    """Wrapper sync function for GET /project/{key}"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_project(project_key=project_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_projects_from_list(
    project_keys: list[str], expand: dict | None = None
) -> ListResponses:
    """Wrapper async function for multiple calls on GET /project/{key}"""
    if expand is None:
        expand = {}
    try:
        tasks = [
            asyncio.create_task(async_fetch_project(project_key=key, expand=expand))
            for key in project_keys
        ]
        return await asyncio.gather(*tasks)
    except exceptions.InvalidResponseError:
        return []


def fetch_projects_from_list(project_keys: list[str], expand: dict | None = None) -> ListResponses:
    """Wrapper sync function for multiple calls on GET /project/{key}"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_projects_from_list(project_keys=project_keys, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_issue(issue_key: str, expand: dict | None = None) -> SingleResponse:
    """Wrapper async function for GET /issue/{key}"""
    method = "GET"
    resource = f"issue/{issue_key}"
    if expand is None:
        expand = {}
    try:
        response = await rest.send_single_request(method=method, resource=resource, params=expand)
        return conversions.process_single_nonpaginated_resource(responses=response)
    except exceptions.InvalidResponseError:
        return {}


def fetch_issue(issue_key: str, expand: dict | None = None) -> SingleResponse:
    """Wrapper sync function for GET /issue/{key}"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_issue(issue_key=issue_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_search_issues(
    jql: str, expand: dict | None = None, field: str | None = None
) -> ListResponses:
    """Wrapper async function for POST /search"""
    method = "POST"
    resource = "search"
    if expand is None:
        expand = {}
    content = {"jql": jql}
    field_array = field
    payload = rest.generate_payload(content)
    try:
        response = await rest.send_paginated_requests(
            method=method, resource=resource, params=expand, payload=payload
        )
        return conversions.process_multiple_paginated_resources(
            responses=response, field_array=field_array
        )
    except exceptions.InvalidResponseError:
        return []


def search_issues(jql: str, expand: dict | None = None, field: str | None = None) -> ListResponses:
    """Wrapper sync function for POST /search"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_search_issues(jql=jql, expand=expand, field=field)
    return loop.run_until_complete(coroutine)
