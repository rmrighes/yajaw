import asyncio
import httpx

# 3.13? from warnings import deprecated
from .configuration import *


#######################################
# Auxiliary Functions
#######################################


def convert_gathered_responses_to_json(group_resp) -> list[any]:
    converted_list = list()
    for task_resp in group_resp:
        converted_list.append(task_resp.json())
    return converted_list


async def slowdown_if_needed(resp) -> None:
    if int(resp.headers["x-ratelimit-remaining"]) < 25:
        await asyncio.sleep(0.3)  # rate limiting control


def is_success_response(resp) -> bool:
    if resp.status_code == httpx.codes.OK:
        return True
    return False


def rate_limit_reached(attempts: int) -> bool:
    if attempts >= 10:
        return True
    return False


def retry_request(resp, attempts) -> bool:
    log_message = f"Status Code: {
        resp.status_code} -- attempt {attempts:02d} -- {resp.request.method} {resp.request.url}"
    if rate_limit_reached(attempts):
        retry = False
        logger.error(log_message)
    elif is_success_response(resp):
        retry = False
        logger.info(log_message)
    else:
        retry = True
        logger.warning(log_message)
    return retry


def convert_response_obj_to_dict(
    resp: list[httpx.Response] | httpx.Response,
) -> list[dict[any]] | dict[any]:
    if isinstance(resp, httpx.Response):
        result = resp.json()
    elif isinstance(resp, list):
        result = list()
        for single_response in resp:
            result.append(single_response.json())
    return result


def extract_values_from_key_in_list_of_dict(
    grouped_response: list[dict[any]], key: str
) -> list[any]:
    r = list()
    for single_group in grouped_response:
        for item in single_group[key]:
            r.append(item)
    return r


#######################################
# REST Calls
#######################################


def set_request_headers() -> dict[any]:
    return {"Accept": "application/json", "Authorization": f"Bearer {JIRA_PAT}"}


async def send_request(
    client: httpx.AsyncClient = None,
    semaphore: asyncio.BoundedSemaphore = None,
    method: str = None,
    url: str = None,
    headers: dict = None,
    params: dict = None,
    payload: dict = None,
) -> httpx.Response:
    async with semaphore:
        attempts = 0
        retry = True
        while retry:
            response = await client.request(
                method=method, url=url, headers=headers, params=params, json=payload
            )
            attempts += 1
            # TODO: check if a valid httpx.Response object was returned
            await slowdown_if_needed(response)
            retry = retry_request(response, attempts)
    return response


# TODO: Calls to next page are sequential.
# It can be improved to become concurrent at the pagination level after the first call.
async def send_request_paginated(
    client: httpx.AsyncClient = None,
    semaphore: asyncio.BoundedSemaphore = None,
    method: str = None,
    url: str = None,
    headers: dict = None,
    params: dict = None,
    payload: dict = None,
) -> list[httpx.Response]:
    result = list()
    startAt = payload["startAt"]
    maxResults = payload["maxResults"]
    more_pages = True
    counter = 0
    while more_pages:
        response = await send_request(
            client=client,
            semaphore=semaphore,
            method=method,
            url=url,
            headers=headers,
            params=params,
            payload=payload,
        )
        result.append(response)

        counter += 1
        total = response.json()["total"]

        logger.info(f"Page {counter} - startAt {startAt} - total {total}")
        logger.info(payload)
        if total < (startAt + maxResults):
            more_pages = False
        else:
            startAt = startAt + maxResults
            payload["startAt"] = startAt

    return result


#######################################
# Jira API
#######################################


# 3.13? @deprecated("Use Get projects paginated that supports search and pagination")
async def get_all_projects() -> list[any]:
    headers = set_request_headers()
    async with httpx.AsyncClient(verify=False) as client:
        task = asyncio.create_task(
            send_request(
                client=client,
                semaphore=semaphore,
                method="GET",
                url=f"{JIRA_BASE_URL}/{JIRA_API}/project",
                headers=headers,
            )
        )
        responses = await task
    return responses.json()


async def get_project(key=str) -> dict[any]:
    headers = set_request_headers()
    async with httpx.AsyncClient(verify=False) as client:
        task = asyncio.create_task(
            send_request(
                client=client,
                semaphore=semaphore,
                method="GET",
                url=f"{JIRA_BASE_URL}/{JIRA_API}/project/{key}",
                headers=headers,
            )
        )
        response = await task
    return response.json()


async def get_projects_from_list(keys=list[str]) -> list[any]:
    headers = set_request_headers()
    async with httpx.AsyncClient(verify=False) as client:
        tasks = [
            asyncio.create_task(
                send_request(
                    client=client,
                    semaphore=semaphore,
                    method="GET",
                    url=f"{JIRA_BASE_URL}/{JIRA_API}/project/{key}",
                    headers=headers,
                )
            )
            for key in keys
        ]
        group_responses = await asyncio.gather(*tasks)
    return convert_response_obj_to_dict(group_responses)


async def search_issues_jql(jql: str = None) -> list[any]:
    headers = set_request_headers()
    payload = {"jql": f"{jql}", "startAt": 0, "maxResults": 50}
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        task = asyncio.create_task(
            send_request_paginated(
                client=client,
                semaphore=semaphore,
                method="POST",
                url=f"{JIRA_BASE_URL}/{JIRA_API}/search",
                headers=headers,
                payload=payload,
            )
        )
        response = await task
        processed_response = convert_response_obj_to_dict(response)
        issues = list()
        issues = extract_values_from_key_in_list_of_dict(
            processed_response, "issues")
        return issues


def get_next_project_jql(project_key: str):
    return f"project = {project_key}"


def flatten_list_of_dictionaries(input_list: list[list[dict[any]]]) -> list[dict]:
    flattened_list = list()
    for nested_list in input_list:
        for item in nested_list:
            flattened_list.append(item)
    return flattened_list


async def get_issues_from_project(key: str | list[str]) -> list[any]:
    # A single string with a project key
    if isinstance(key, str):
        jql = get_next_project_jql(key)
        return await search_issues_jql(jql=jql)
    # A list of strings with project keys
    elif isinstance(key, list):
        tasks = [
            asyncio.create_task(search_issues_jql(
                jql=get_next_project_jql(next_key)))
            for next_key in key
        ]
        list_responses = await asyncio.gather(*tasks)
        return flatten_list_of_dictionaries(list_responses)
