from yajaw.core import rest
from yajaw.utils import conversions
import asyncio

type list_responses = list[dict[any]]
type single_response = dict[any]


def fetch_all_projects(expand: str = None) -> list_responses:
    method = "GET"
    resource = "project"
    # Enable a synchronous function execute an asynchronous one
    loop = asyncio.get_event_loop()
    coroutine = rest.send_concurrent_requests(method=method, resource=resource)
    loop_result = loop.run_until_complete(coroutine)
    projects = conversions.process_responses(responses=loop_result, list_resources=True)
    return projects


def fetch_project(project_key: str, expand: str = None) -> single_response:
    method = "GET"
    resource = f"project/{project_key}"
    # Enable a synchronous function execute an asynchronous one
    loop = asyncio.get_event_loop()
    coroutine = rest.send_concurrent_requests(method=method, resource=resource)
    loop_result = loop.run_until_complete(coroutine)
    project = conversions.process_responses(responses=loop_result, list_resources=False)
    return project


def fetch_projects_from_list(
    project_keys: list[str], expand: str = None
) -> list_responses:
    ...


def fetch_issue(
    issue_key: str, expand: str = None, fields: str = None
) -> single_response:
    ...


def search_issues(
    jql: str, expand: str = None, fields: str = None
) -> list_responses:
    ...


def fetch_all_issues_from_projects(
    project_keys: list[str], expand: str = None, fields: str = None
) -> list_responses:
    ...
