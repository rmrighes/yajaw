""" Module responsible for the externally accessible functions wrapping 
the Jira API."""
import asyncio

from yajaw.core import rest
from yajaw.utils import conversions

type list_responses = list[dict[any]]
type single_response = dict[any]


async def async_fetch_all_projects(expand: dict = None) -> list_responses:
    """Wrapper async function for GET /project"""
    method = "GET"
    resource = "project"
    if expand is None:
        expand = {}
    response = await rest.send_single_request(
        method=method, resource=resource, params=expand
    )
    projects = conversions.process_multiple_nonpaginated_resources(responses=response)
    return projects


def fetch_all_projects(expand: dict = None) -> list_responses:
    """Wrapper sync function for GET /project"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_all_projects(expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_project(project_key: str, expand: dict = None) -> single_response:
    """Wrapper async function for GET /project/{key}"""
    method = "GET"
    resource = f"project/{project_key}"
    if expand is None:
        expand = {}
    response = await rest.send_single_request(
        method=method, resource=resource, params=expand
    )
    project = conversions.process_single_nonpaginated_resource(responses=response)
    return project


def fetch_project(project_key: str, expand: dict = None) -> single_response:
    """Wrapper sync function for GET /project/{key}"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_project(project_key=project_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_projects_from_list(
    project_keys: list[str], expand: dict = None
) -> list_responses:
    """Wrapper async function for multiple calls on GET /project/{key}"""
    if expand is None:
        expand = {}
    tasks = [
        asyncio.create_task(async_fetch_project(project_key=key, expand=expand))
        for key in project_keys
    ]
    response = await asyncio.gather(*tasks)
    return response


def fetch_projects_from_list(
    project_keys: list[str], expand: dict = None
) -> list_responses:
    """Wrapper sync function for multiple calls on GET /project/{key}"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_projects_from_list(project_keys=project_keys, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_issue(issue_key: str, expand: dict = None) -> single_response:
    """Wrapper async function for GET /issue/{key}"""
    method = "GET"
    resource = f"issue/{issue_key}"
    if expand is None:
        expand = {}
    response = await rest.send_single_request(
        method=method, resource=resource, params=expand
    )
    issue = conversions.process_single_nonpaginated_resource(responses=response)
    return issue


def fetch_issue(issue_key: str, expand: dict = None) -> single_response:
    """Wrapper sync function for GET /issue/{key}"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_issue(issue_key=issue_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_search_issues(
    jql: str, expand: dict = None, field: str = None
) -> list_responses:
    """Wrapper async function for POST /search"""
    method = "POST"
    resource = "search"
    if expand is None:
        expand = {}
    content = {"jql": jql}
    field_array = field
    payload = rest.generate_payload(content)
    response = await rest.send_paginated_requests(
        method=method, resource=resource, params=expand, payload=payload
    )
    issues = conversions.process_multiple_paginated_resources(
        responses=response, field_array=field_array
    )
    return issues


def search_issues(jql: str, expand: dict = None, field: str = None) -> list_responses:
    """Wrapper sync function for POST /search"""
    if expand is None:
        expand = {}
    loop = asyncio.new_event_loop()
    coroutine = async_search_issues(jql=jql, expand=expand, field=field)
    return loop.run_until_complete(coroutine)
