import httpx
import json

type list_responses = list[dict[any]]
type single_response = dict[any]


def validate_responses_attribute(responses: list[httpx.Response]) -> None:
    if isinstance(responses, list):
        if all(isinstance(response, httpx.Response) for response in responses):
            return None
    raise InvalidResponseException


def process_single_nonpaginated_resource(responses: list[httpx.Response]):
    validate_responses_attribute(responses=responses)
    consolidated_responses = responses[0].json()
    return consolidated_responses


def process_multiple_nonpaginated_resources(responses: list[httpx.Response]):
    validate_responses_attribute(responses=responses)
    consolidated_responses = [
        resource for response in responses for resource in response.json()
    ]
    return consolidated_responses


def process_multiple_paginated_resources(responses: list[httpx.Response], field: str):
    validate_responses_attribute(responses=responses)
    consolidated_responses = list()
    for single_response in responses:
        resources = single_response.json()
        for resource in resources[field]:
            consolidated_responses.append(resource)
    return consolidated_responses


class InvalidResponseException(Exception):
    "Response is not valid!"
