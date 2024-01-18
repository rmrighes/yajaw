"""TBD"""
import asyncio

from yajaw import ApiType, YajawConfig
from yajaw.core import exceptions as e
from yajaw.core import rest


async def async_fetch_all_projects(expand: str | None = None) -> list[dict]:
    """TBD"""
    expand_dict = {} if expand is None else {"expand": expand}

    info = {
        "method": "GET",
        "resource": "project",
        "api": YajawConfig.SERVER_API,
        "params": expand_dict,
        "payload": None,
    }

    jira = rest.JiraInfo(info=info)

    try:
        response = await rest.send_single_request(jira=jira)
        return response.json()
    except e.ResourceNotFoundError:
        return []


def fetch_all_projects(expand: str | None = None) -> list[dict]:
    """Wrapper sync function for GET /project"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    coroutine = async_fetch_all_projects(expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_project(project_key: str, expand: str | None = None) -> dict:
    """TBD"""
    expand_dict = {} if expand is None else {"expand": expand}

    info = {
        "method": "GET",
        "resource": f"project/{project_key}",
        "api": YajawConfig.SERVER_API,
        "params": expand_dict,
        "payload": None,
    }

    jira = rest.JiraInfo(info=info)

    try:
        response = await rest.send_single_request(jira=jira)
        return response.json()
    except e.ResourceNotFoundError:
        return {}


def fetch_project(project_key: str, expand: str | None = None) -> dict:
    """Wrapper sync function for GET /project/{key}"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    coroutine = async_fetch_project(project_key=project_key, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_projects_from_list(
    project_keys: list[str], expand: str | None = None
) -> list[dict]:
    """TBD"""
    expand_dict = {} if expand is None else {"expand": expand}

    info_list = [
        {
            "method": "GET",
            "resource": f"project/{project_key}",
            "api": YajawConfig.SERVER_API,
            "params": expand_dict,
            "payload": None,
        }
        for project_key in project_keys
    ]

    jira_list = [rest.JiraInfo(info=info) for info in info_list]

    try:
        tasks = [asyncio.create_task(rest.send_single_request(jira=jira)) for jira in jira_list]
        responses = await asyncio.gather(*tasks)
        return [response.json() for response in responses]
    except e.ResourceNotFoundError:
        return []


def fetch_projects_from_list(project_keys: list[str], expand: str | None = None) -> list[dict]:
    """Wrapper sync function for multiple calls on GET /project/{key}"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    coroutine = async_fetch_projects_from_list(project_keys=project_keys, expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_issue(
    issue_key: str, expand: str | None = None, agile: ApiType = ApiType.CLASSIC
) -> dict:
    """TBD"""
    expand_dict = {} if expand is None else {"expand": expand}

    api = YajawConfig.SERVER_API if not agile else YajawConfig.AGILE_API

    info = {
        "method": "GET",
        "resource": f"issue/{issue_key}",
        "api": api,
        "params": expand_dict,
        "payload": None,
    }

    jira = rest.JiraInfo(info=info)

    try:
        response = await rest.send_single_request(jira=jira)
        return response.json()
    except e.ResourceNotFoundError:
        return {}


def fetch_issue(
    issue_key: str, expand: str | None = None, agile: ApiType = ApiType.CLASSIC
) -> dict:
    """Wrapper sync function for GET /issue/{key}"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    coroutine = async_fetch_issue(issue_key=issue_key, expand=expand, agile=agile)
    return loop.run_until_complete(coroutine)


async def async_search_issues(jql: str, expand: str | None = None) -> list[dict]:
    """TBD"""
    expand_dict = {} if expand is None else {"expand": expand}
    query = {"jql": jql}

    info = {
        "method": "POST",
        "resource": "search",
        "api": YajawConfig.SERVER_API,
        "params": expand_dict,
        "payload": query,
    }

    jira = rest.JiraInfo(info=info)

    try:
        responses = await rest.send_paginated_requests(jira=jira)
        return [issue for issue_page in responses for issue in issue_page.json()["issues"]]
    except e.ResourceNotFoundError:
        return []


def search_issues(jql: str, expand: str | None = None) -> list[dict]:
    """Wrapper sync function for POST /search"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    coroutine = async_search_issues(jql=jql, expand=expand)
    return loop.run_until_complete(coroutine)
