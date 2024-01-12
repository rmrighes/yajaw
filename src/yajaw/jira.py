import asyncio
from yajaw.core import rest
from yajaw.core import exceptions as e


async def async_fetch_all_projects(expand: dict | None = None) -> list[dict]:
    expand = {} if expand is None else None
    jira = rest.JiraInfo(method="GET", resource="project", params=expand, payload=None)
    try:
        response = await rest.send_single_request(jira=jira)
        return response.json()
    except e.ResourceNotFoundError as exc:
        return []


def fetch_all_projects(expand: dict | None = None) -> list[dict]:
    """Wrapper sync function for GET /project"""
    expand = {} if expand is None else None
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_all_projects(expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_project(project_key: str, expand: dict | None = None) -> dict:
    expand = {} if expand is None else None
    jira = rest.JiraInfo(
        method="GET", resource=f"project/{project_key}", params=expand, payload=None
    )
    try:
        response = await rest.send_single_request(jira=jira)
        return response.json()
    except e.ResourceNotFoundError as exc:
        return {}


def fetch_project(project_key: str, expand: dict | None = None) -> dict:
    """Wrapper sync function for GET /project/{key}"""
    expand = {} if expand is None else None
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_project(project_key=project_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_projects_from_list(
    project_keys: list[str], expand: dict | None = None
) -> dict:
    expand = {} if expand is None else None

    jira_list = [
        rest.JiraInfo(
            method="GET",
            resource=f"project/{project_key}",
            params=expand,
            payload=None,
        )
        for project_key in project_keys
    ]

    try:
        tasks = [
            asyncio.create_task(rest.send_single_request(jira=jira))
            for jira in jira_list
        ]
        responses = await asyncio.gather(*tasks)
        return [response.json() for response in responses]
    except e.ResourceNotFoundError as exc:
        return []


def fetch_projects_from_list(project_keys: list[str], expand: dict | None = None) -> list[dict]:
    """Wrapper sync function for multiple calls on GET /project/{key}"""
    expand = {} if expand is None else None
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_projects_from_list(project_keys=project_keys, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_issue(issue_key: str, expand: dict | None = None) -> dict:
    expand = {} if expand is None else None
    jira = rest.JiraInfo(
        method="GET", resource=f"issue/{issue_key}", params=expand, payload=None
    )
    try:
        response = await rest.send_single_request(jira=jira)
        return response.json()
    except e.ResourceNotFoundError as exc:
        return {}


def fetch_issue(issue_key: str, expand: dict | None = None) -> dict:
    """Wrapper sync function for GET /issue/{key}"""
    expand = {} if expand is None else None
    loop = asyncio.new_event_loop()
    coroutine = async_fetch_issue(issue_key=issue_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_search_issues(jql: str, expand: dict | None = None) -> list[dict]:
    expand = {} if expand is None else None
    query = {"jql": jql}
    jira = rest.JiraInfo(
        method="POST", resource=f"search", params=expand, payload=query
    )

    try:
        responses = await rest.send_paginated_requests(jira=jira)
        return [issue for issue_page in responses for issue in issue_page.json()["issues"]]
    except e.ResourceNotFoundError as exc:
        return []


def search_issues(jql: str, expand: dict | None = None, field: str | None = None) -> list[dict]:
    """Wrapper sync function for POST /search"""
    expand = {} if expand is None else None
    loop = asyncio.new_event_loop()
    coroutine = async_search_issues(jql=jql, expand=expand)
    return loop.run_until_complete(coroutine)