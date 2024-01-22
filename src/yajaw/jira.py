"""
Module wrapping up the supported Jira resources.
It is the external interface for yajaw users.
"""
import asyncio

from yajaw import ApiType, YajawConfig
from yajaw import exceptions as e
from yajaw.core import rest
from yajaw.utils.concurrency import async_to_sync


async def async_fetch_all_projects(expand: str | None = None) -> list[dict]:
    """
    async_fetch_all_projects Async call to fetch all projects.

    It is intended to be used on asynchronous code. Use the sync version otherwise.
    Returns all projects visible to the user. It is based on the API
    GET /rest/api/2/project. That resource is deprecated and will be replaced
    by GET /rest/api/2/project/search, which will support pagination.


    Args:
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: description, issueTypes, lead,
        and projectKeys.

    Returns:
        list[dict]: List of dictionaries representing the returned projects.
        An empty list is returned if nothing found.
    """
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


@async_to_sync
def fetch_all_projects(expand: str | None = None) -> list[dict]:
    """
    fetch_all_projects Sync call to fetch all projects.

    It is intended to be used on synchronous code. Use the async version otherwise.
    Returns all projects visible to the user. It is based on the API
    GET /rest/api/2/project. That resource is deprecated and will be replaced
    by GET /rest/api/2/project/search, which will support pagination.


    Args:
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: description, issueTypes, lead,
        and projectKeys.

    Returns:
        list[dict]: List of dictionaries representing the returned projects.
        An empty list is returned if nothing found.
    """
    return async_fetch_all_projects(expand=expand)


async def async_fetch_project(project_key: str, expand: str | None = None) -> dict:
    """
    async_fetch_project Async call to fetch the details of a single project.

     It is intended to be used on asynchronous code. Use the sync version otherwise.
     Return the details of a single project. It is based on the API
     GET /rest/api/2/project/{projectKey}.

    Args:
        project_key (str): Key identifier for the project.
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: description, issueTypes, lead,
        projectKeys, and issueTypeHierarchy. Defaults to None.

    Returns:
        dict: Dictionary with the project details. An empty dictionary is returned
        if nothing is found.
    """
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


@async_to_sync
def fetch_project(project_key: str, expand: str | None = None) -> dict:
    """
    fetch_project Sync call to fetch the details of a single project.

     It is intended to be used on synchronous code. Use the async version otherwise.
     Return the details of a single project. It is based on the API
     GET /rest/api/2/project/{projectKey}.

    Args:
        project_key (str): Key identifier for the project.
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: description, issueTypes, lead,
        projectKeys, and issueTypeHierarchy. Defaults to None.

    Returns:
        dict: Dictionary with the project details. An empty dictionary is returned
        if nothing is found.
    """
    return async_fetch_project(project_key=project_key, expand=expand)


async def async_fetch_projects_from_list(
    project_keys: list[str], expand: str | None = None
) -> list[dict]:
    """
    async_fetch_projects_from_list Async call to fetch the details of a list of projects.

    It is intended to be used on asynchronous code. Use the sync version otherwise.
    Return the details of a list of projects. It is based on the API
    GET /rest/api/2/project/{projectKey} and the function calls it as many times as
    items in the provided list.

    Args:
        project_keys (list[str]): A list of strings representing the project keys.
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: description, issueTypes, lead,
        projectKeys, and issueTypeHierarchy. Defaults to None.

    Returns:
        list[dict]: List of dictionaries representing the returned projects.
        An empty list is returned if nothing found.
    """
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


@async_to_sync
def fetch_projects_from_list(project_keys: list[str], expand: str | None = None) -> list[dict]:
    """
    fetch_projects_from_list Sync call to fetch the details of a list of projects.

    It is intended to be used on synchronous code. Use the async version otherwise.
    Return the details of a list of projects. It is based on the API
    GET /rest/api/2/project/{projectKey} and the function calls it as many times as
    items in the provided list.

    Args:
        project_keys (list[str]): A list of strings representing the project keys.
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: description, issueTypes, lead,
        projectKeys, and issueTypeHierarchy. Defaults to None.

    Returns:
        list[dict]: List of dictionaries representing the returned projects.
        An empty list is returned if nothing found.
    """
    return async_fetch_projects_from_list(project_keys=project_keys, expand=expand)


async def async_fetch_issue(
    issue_key: str, expand: str | None = None, agile: ApiType = ApiType.CLASSIC
) -> dict:
    """
    async_fetch_issue  Async call to fetch the details of a single issue.

    It is intended to be used on asynchronous code. Use the sync version otherwise.
    Return the details of a single issue. It is based on the API
    GET /rest/api/2/issue/{issueKey}. If the identifier doesn't match an issue,
    a case-insensitive search and check for moved issues is performed.
    If a matching issue is found its details are returned.

    Args:
        issue_key (str):  Key identifier for the issue.
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: renderedFields, name, schema,
        transitions,editmeta, changelog, and versionedRepresentations.
        Defaults to None.
        agile (ApiType, optional): Takes the enumeration values ApiType.CLASSIC or
        ApiType.AGILE as possible values to represent which API to be used. Defaults
        to ApiType.CLASSIC.

    Returns:
        dict: Dictionary with the issue details. An empty dictionary is returned
        if nothing is found.
    """
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


@async_to_sync
def fetch_issue(
    issue_key: str, expand: str | None = None, agile: ApiType = ApiType.CLASSIC
) -> dict:
    """
    fetch_issue  Sync call to fetch the details of a single issue.

    It is intended to be used on synchronous code. Use the async version otherwise.
    Return the details of a single issue. It is based on the API
    GET /rest/api/2/issue/{issueKey}. If the identifier doesn't match an issue,
    a case-insensitive search and check for moved issues is performed.
    If a matching issue is found its details are returned.

    Args:
        issue_key (str):  Key identifier for the issue.
        expand (str | None, optional): Expect a simple string with a comma-separated
        list of attributes to be expanded. They are: renderedFields, name, schema,
        transitions,editmeta, changelog, and versionedRepresentations.
        Defaults to None.
        agile (ApiType, optional): Takes the enumeration values ApiType.CLASSIC or
        ApiType.AGILE as possible values to represent which API to be used. Defaults
        to ApiType.CLASSIC.

    Returns:
        dict: Dictionary with the issue details. An empty dictionary is returned
        if nothing is found.
    """
    return async_fetch_issue(issue_key=issue_key, expand=expand, agile=agile)


async def async_search_issues(jql: str, expand: str | None = None) -> list[dict]:
    """
    async_search_issues Async call to fetch the result of a search for issues using JQL.

    It is intended to be used on asynchronous code. Use the sync version otherwise.
    Return the results of a search for issues using the provided JQL. It is based on
    the API POST /rest/api/2/search.

    Args:
        jql (str): _description_
        expand (str | None, optional): _description_. Defaults to None.

    Returns:
        list[dict]: list[dict]: List of dictionaries representing the returned projects.
        An empty list is returned if nothing found.
    """
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


@async_to_sync
def search_issues(jql: str, expand: str | None = None) -> list[dict]:
    """
    search_issues Sync call to fetch the result of a search for issues using JQL.

    It is intended to be used on synchronous code. Use the async version otherwise.
    Return the results of a search for issues using the provided JQL. It is based on
    the API POST /rest/api/2/search.

    Args:
        jql (str): _description_
        expand (str | None, optional): _description_. Defaults to None.

    Returns:
        list[dict]: list[dict]: List of dictionaries representing the returned projects.
        An empty list is returned if nothing found.
    """
    return async_search_issues(jql=jql, expand=expand)
