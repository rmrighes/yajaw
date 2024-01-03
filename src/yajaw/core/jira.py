from yajaw.core import rest
import asyncio

type list_responses = list[dict[any]]
type single_response = dict[any]


def fetch_all_projects(expand: str = None) -> list_responses:
    method = "GET"
    resource = "project"
    # Enable a synchronous function execute an asynchronous one
    loop = asyncio.get_event_loop()
    coroutine = rest.send_paginated_request(method=method, resource=resource)
    projects = loop.run_until_complete(coroutine)
    return projects


async def fetch_project(project_key: str, expand: str = None) -> single_response:
    ...


async def fetch_projects_from_list(
    project_keys: list[str], expand: str = None
) -> list_responses:
    ...


async def fetch_issue(
    issue_key: str, expand: str = None, fields: str = None
) -> single_response:
    ...


async def search_issues(
    jql: str, expand: str = None, fields: str = None
) -> list_responses:
    ...


async def fetch_all_issues_from_projects(
    project_keys: list[str], expand: str = None, fields: str = None
) -> list_responses:
    ...
