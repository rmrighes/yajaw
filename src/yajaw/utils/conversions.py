"""Module responsible for conversion and basic clean up functions."""
import httpx

from yajaw.core import exceptions

type list_responses = list[dict[any]]
type single_response = dict[any]


def validate_responses_attribute(responses: list[httpx.Response]) -> None:
    """Ensures the responses are a non-empty list of httpx.Response objects.
    """
    if isinstance(responses, list):
        if len(responses) > 0:
            if all(isinstance(response, httpx.Response) for response in responses):
                return None
    raise exceptions.InvalidResponseException


def process_single_nonpaginated_resource(responses: list[httpx.Response]) -> single_response:
    """Ensure that an original list of a single httpx.Response object is
    converted into a dictionary, as it is the expected format for a
    single response with a single resource.
    """
    validate_responses_attribute(responses=responses)
    if len(responses) == 1:
        consolidated_responses = responses[0].json()
        return consolidated_responses
    else:
        raise exceptions.InvalidResponseException


def process_multiple_nonpaginated_resources(responses: list[httpx.Response]):
    """Ensure that an original list of multiple httpx.Response objects is
    converted into a list of dictionaries, as it is the expected format for
    a single response with multiple resources.
    """
    validate_responses_attribute(responses=responses)
    consolidated_responses = [
        resource for response in responses for resource in response.json()
    ]
    return consolidated_responses


def process_multiple_paginated_resources(responses: list[httpx.Response], field_array: str):
    """Ensure that an original list of multiple httpx.Response objects is
    converted into a list of dictionaries, as it is the expected format for
    a single response with multiple resources. It flattens the response if
    multiple resources are part of a single response.
    """
    validate_responses_attribute(responses=responses)
    consolidated_responses = list()
    for single_response in responses:
        resources = single_response.json()
        for resource in resources[field_array]:
            consolidated_responses.append(resource)
    return consolidated_responses
