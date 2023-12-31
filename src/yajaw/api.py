import asyncio
import httpx
#3.13? from warnings import deprecated
from .configuration import *


#######################################
# Auxiliary Functions
#######################################


def flatten_gathered_responses(group_resp) -> list:
    flatten_resp = list()
    for task_resp in group_resp:
        for resp in task_resp.json():
            flatten_resp.append(resp)
    return flatten_resp


def convert_gathered_responses_to_json(group_resp) -> list:
    converted_list = list()
    for task_resp in group_resp:
        converted_list.append(task_resp.json())
    return converted_list


async def slowdown_if_needed(resp) -> None:
    if int(resp.headers["x-ratelimit-remaining"]) < 25:
        await asyncio.sleep(0.3) # rate limiting control

def is_success_response(resp) -> bool:
    if resp.status_code == httpx.codes.OK:
        return True
    return False


def rate_limit_reached(attempts: int) -> bool:
    if attempts >= 99: 
        return False
    return True

def retry_request(resp, attempts) -> bool:
    log_message = f"Status Code: {resp.status_code} -- attempt {attempts:02d} -- {resp.request.method} {resp.request.url}"
    if not rate_limit_reached(attempts):
        retry = False
        logger.error(log_message)
    elif is_success_response(resp):
        retry = False
        logger.info(log_message)
    else:
        retry = True
        logger.warning(log_message)
    return retry

#######################################
# REST Calls
#######################################


def set_request_headers() -> dict:
    return { "Accept": "application/json",
          "Authorization": f"Bearer {JIRA_PAT}"} 


async def send_request(client: httpx.AsyncClient, 
                       semaphore: asyncio.BoundedSemaphore, 
                       method: str, 
                       url: str, 
                       headers: dict) -> httpx.Response:

    async with semaphore:

        attempts = 0
        retry = True
        
        while retry:
        
            response = await client.request(method = method, 
                                            url = url, 
                                            headers = headers)
            attempts += 1
            await slowdown_if_needed(response)
            retry = retry_request(response, attempts)

    return response

#######################################
# Jira API
#######################################


#3.13? @deprecated("Use Get projects paginated that supports search and pagination")
async def get_all_projects() -> list:
    headers = set_request_headers()
    async with httpx.AsyncClient() as client:
        task = asyncio.create_task(send_request(client=client, 
                                                semaphore=semaphore,
                                                method="GET",
                                                url=f"{JIRA_BASE_URL}/{JIRA_API}/project", 
                                                headers=headers))
        responses = await task
    return responses.json()


async def get_project(key=str) -> dict:
    headers = set_request_headers()
    async with httpx.AsyncClient() as client:
        task = asyncio.create_task(send_request(client=client, 
                                                semaphore=semaphore,
                                                method="GET",
                                                url=f"{JIRA_BASE_URL}/{JIRA_API}/project/{key}", 
                                                headers=headers))
        response = await task
    return response.json()


async def get_projects_from_list(keys=list[str]) -> list:
    headers = set_request_headers()
    async with httpx.AsyncClient() as client:
        tasks = [ asyncio.create_task(send_request(client=client, 
                                                   semaphore=semaphore,
                                                   method="GET",
                                                   url=f"{JIRA_BASE_URL}/{JIRA_API}/project/{key}", 
                                                   headers=headers)) for key in keys]
        group_responses = await asyncio.gather(*tasks)
    return convert_gathered_responses_to_json(group_responses)