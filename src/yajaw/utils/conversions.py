"""Module responsible for conversion and basic clean up functions."""
import httpx

from yajaw.core import exceptions

type ListResponses = list[dict[any]]
type SingleResponse = dict[any]


def validate_responses_attribute(responses: list[httpx.Response]) -> None:
    """Ensures the responses are a non-empty list of httpx.Response objects."""

    if (
        not isinstance(responses, list)
        or not len(responses) > 0
        or not all(isinstance(response, httpx.Response) for response in responses)
    ):
        raise exceptions.InvalidResponseError

    # if isinstance(responses, list):
    #    if len(responses) > 0:
    #        if all(isinstance(response, httpx.Response) for response in responses):
    #            return None
    # raise exceptions.InvalidResponseError


def process_single_nonpaginated_resource(
    responses: list[httpx.Response],
) -> SingleResponse:
    """Ensure that an original list of a single httpx.Response object is
    converted into a dictionary, as it is the expected format for a
    single response with a single resource.
    """
    validate_responses_attribute(responses=responses)
    if len(responses) == 1:
        return responses[0].json()
    raise exceptions.InvalidResponseError


def process_multiple_nonpaginated_resources(
    responses: list[httpx.Response],
) -> ListResponses:
    """Ensure that an original list of multiple httpx.Response objects is
    converted into a list of dictionaries, as it is the expected format for
    a single response with multiple resources.
    """
    validate_responses_attribute(responses=responses)
    return [resource for response in responses for resource in response.json()]


def process_multiple_paginated_resources(
    responses: list[httpx.Response], field_array: str
) -> ListResponses:
    """Ensure that an original list of multiple httpx.Response objects is
    converted into a list of dictionaries, as it is the expected format for
    a single response with multiple resources. It flattens the response if
    multiple resources are part of a single response.
    """
    validate_responses_attribute(responses=responses)

    # consolidated_responses = []

    # Direct way: Nested For-loop
    # for one_response in responses:
    #    resources = one_response.json()
    #    for resource in resources[field_array]:
    #        consolidated_responses.append(resource)

    # Alternative option: Pythonic way with list comprehension
    return [resource for resource_set in responses for resource in resource_set.json()[field_array]]
