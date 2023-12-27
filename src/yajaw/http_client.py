import asyncio
import requests

# For context: https://github.com/python/typing/issues/182
# TypeAlias is deprecated since version 3.12

# Type statement is new to version 3.12. 
# type JSON = int | str | float | bool | None | dict[str, "JSON"] | list["JSON"]
# type JSONObject = dict[str, JSON]
# type JSONList = list[JSON]

# For backwards compatibility, type aliases can also be created through simple assignment.
JSON = int | str | float | bool | None | dict[str, "JSON"] | list["JSON"]
JSONDictionary = dict[str, JSON]
JSONList = list[JSON]

def http_method_sync(method: str, url: str) -> JSON:
    headers = {
        "Accept": "application/json"
    }
    auth = None
    response = requests.request(
        method,
        url,
        headers=headers,
        auth = auth
    )
    return response.json()

async def http_method_async(method: str, url: str) -> JSON:
    return await asyncio.to_thread(http_method_sync, method, url)
