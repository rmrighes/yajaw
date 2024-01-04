from yajaw.core import rest
from yajaw.utils import conversions
import asyncio

type list_responses = list[dict[any]]
type single_response = dict[any]


async def async_fetch_all_projects(expand: str = None) -> list_responses:
    method = "GET"
    resource = "project"
    response = await rest.send_single_request(method=method, resource=resource)
    projects = conversions.process_multiple_nonpaginated_resources(responses=response)
    return projects


def fetch_all_projects(expand: str = None) -> list_responses:
    loop = asyncio.get_event_loop()
    coroutine = async_fetch_all_projects(expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_project(project_key: str, expand: str = None) -> single_response:
    method = "GET"
    resource = f"project/{project_key}"
    response = await rest.send_single_request(method=method, resource=resource)
    project = conversions.process_single_nonpaginated_resource(responses=response)
    return project


def fetch_project(project_key: str, expand: str = None) -> single_response:
    loop = asyncio.get_event_loop()
    coroutine = async_fetch_project(project_key=project_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_projects_from_list(
    project_keys: list[str], expand: str = None
) -> list_responses:
    tasks = [
        asyncio.create_task(async_fetch_project(project_key=key, expand=expand))
        for key in project_keys
    ]
    response = await asyncio.gather(*tasks)
    return response


def fetch_projects_from_list(
    project_keys: list[str], expand: str = None
) -> list_responses:
    loop = asyncio.get_event_loop()
    coroutine = async_fetch_projects_from_list(project_keys=project_keys, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_issue(
    issue_key: str, expand: str = None, fields: str = None
) -> single_response:
    method = "GET"
    resource = f"issue/{issue_key}"
    response = await rest.send_single_request(method=method, resource=resource)
    issue = conversions.process_single_nonpaginated_resource(responses=response)
    return issue


def fetch_issue(issue_key: str, expand: str = None) -> single_response:
    loop = asyncio.get_event_loop()
    coroutine = async_fetch_issue(issue_key=issue_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_search_issues(
    jql: str, expand: str = None, fields: str = None
) -> list_responses:
    method = "POST"
    resource = f"search"
    content = {"jql": jql}
    field = "issues"
    payload = rest.generate_payload(content)
    response = await rest.send_paginated_requests(
        method=method, resource=resource, payload=payload
    )
    issues = conversions.process_multiple_paginated_resources(
        responses=response, field=field
    )
    return issues


def search_issues(jql: str, expand: str = None, fields: str = None) -> list_responses:
    loop = asyncio.get_event_loop()
    coroutine = async_search_issues(jql=jql, expand=expand, fields=fields)
    return loop.run_until_complete(coroutine)


# Review under this point


def fetch_all_issues_from_projects(
    project_keys: list[str], expand: str = None, fields: str = None
) -> list_responses:
    ...
