from yajaw.core import rest
from yajaw.utils import conversions
import asyncio

type list_responses = list[dict[any]]
type single_response = dict[any]


async def async_fetch_all_projects(expand: str = None) -> list_responses:
    method = "GET"
    resource = "project"
    response = await rest.send_single_request(method=method, resource=resource)
    projects = conversions.process_responses(responses=response, list_resources=True)
    return projects


def fetch_all_projects(expand: str = None) -> list_responses:
    loop = asyncio.get_event_loop()
    coroutine = async_fetch_all_projects(expand=expand)
    return loop.run_until_complete(coroutine)


async def async_fetch_project(project_key: str, expand: str = None) -> single_response:
    method = "GET"
    resource = f"project/{project_key}"
    response = await rest.send_single_request(method=method, resource=resource)
    project = conversions.process_responses(responses=response, list_resources=False)
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
    issue = conversions.process_responses(responses=response, list_resources=False)
    return issue


def fetch_issue(issue_key: str, expand: str = None) -> single_response:
    loop = asyncio.get_event_loop()
    coroutine = async_fetch_issue(issue_key=issue_key, expand=expand)
    return loop.run_until_complete(coroutine)


# Review under this point


def search_issues(jql: str, expand: str = None, fields: str = None) -> list_responses:
    ...


def fetch_all_issues_from_projects(
    project_keys: list[str], expand: str = None, fields: str = None
) -> list_responses:
    ...
