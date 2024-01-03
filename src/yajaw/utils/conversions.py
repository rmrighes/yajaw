import httpx

type list_responses = list[dict[any]]
type single_response = dict[any]


def validate_responses_attribute(responses: list[httpx.Response]) -> None:
    if isinstance(responses, list):
        if all(isinstance(response, httpx.Response) for response in responses):
            return None
    raise InvalidResponseException


def process_responses(
    responses: list[httpx.Response], list_resources: bool
) -> single_response | list_responses:
    validate_responses_attribute(responses)
    processed_responses = convert_responses_to_json(responses)
    if not list_resources and len(processed_responses) == 1:
        processed_responses = processed_responses[0]
    return processed_responses


def convert_responses_to_json(responses: list[httpx.Response]) -> list_responses:
    processed_responses = list()
    for response in responses:
        converted_response = response.json()
        if isinstance(converted_response, dict):
            processed_responses.append(converted_response)
        elif isinstance(converted_response, list):
            [processed_responses.append(resource) for resource in converted_response]
        else:
            raise InvalidResponseException
    return processed_responses


class InvalidResponseException(Exception):
    "Response is not valid!"
