import httpx


def convert_list_of_response_objects_to_list_of_json(
    list_objects: list[httpx.Response],
) -> list[dict[any]]:
    return [convert_response_object_to_json(item) for item in list_objects]


def convert_response_object_to_json(response_object: httpx.Response) -> dict[any]:
    return response_object.json()


def flatten_nested_list(nested_list: list[list[any]]) -> list[any]:
    flat_list = [item for sublist in nested_list for item in sublist]
    return flat_list


def flatten_json(nested_json: dict[any], field: str) -> dict[any]:
    ...


"""
Takes the list of concurrent responses, convert the httpx.Response objects into
JSON (dictionaries) and then flatten the resulting nested lists.

1. List of lists of httpx.Response --> List of lists of JSON
2. List of lists of JSON (dictionaries) --> to List of JSON (dictionaries)
"""


def generate_list_of_responses(responses: list[list[any]]) -> list[dict[any]]:
    list_json = convert_list_of_response_objects_to_list_of_json(responses)
    flatten_list = flatten_nested_list(list_json)
    return flatten_list
