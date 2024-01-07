import httpx
import pytest

from yajaw.core import exceptions as e
from yajaw.utils import conversions


def test_validate_responses_attribute_receives_list_of_response_objs():
    responses = list()
    [
        responses.append(
            httpx.Response(status_code=200, headers=None, request=None, json=None)
        )
        for _ in range(3)
    ]
    result = conversions.validate_responses_attribute(responses=responses)
    assert result == None


def test_validate_responses_attribute_receives_not_list():
    responses = "String"
    with pytest.raises(e.InvalidResponseException):
        conversions.validate_responses_attribute(responses=responses)


def test_validate_responses_attribute_receives_empty_list():
    responses = list()
    with pytest.raises(e.InvalidResponseException):
        conversions.validate_responses_attribute(responses=responses)


def test_validate_responses_attribute_receives_wrong_list_type():
    responses = ["First", "Second", "Third"]
    with pytest.raises(e.InvalidResponseException):
        conversions.validate_responses_attribute(responses=responses)


def test_validate_responses_attribute_receives_list_both_valid_invalid():
    responses = list()
    [
        responses.append(
            httpx.Response(status_code=200, headers=None, request=None, json=None)
        )
        for _ in range(3)
    ]
    responses.append("String")
    with pytest.raises(e.InvalidResponseException):
        conversions.validate_responses_attribute(responses=responses)


def test_process_single_nonpaginated_resource_receives_list_with_single_response_obj():
    responses = list()
    responses.append(
        httpx.Response(
            status_code=200, headers=None, request=None, json={"key": "value"}
        )
    )
    result = conversions.process_single_nonpaginated_resource(responses=responses)
    assert type(result) == dict
    assert result["key"] == "value"


def test_process_single_nonpaginated_resource_receives_list_with_multiple_response_obj():
    responses = list()
    [
        responses.append(
            httpx.Response(
                status_code=200, headers=None, request=None, json={"key": "value"}
            )
        )
        for _ in range(3)
    ]
    with pytest.raises(e.InvalidResponseException):
        conversions.process_single_nonpaginated_resource(responses=responses)


def test_process_single_nonpaginated_resource_receives_wrong_list_type():
    responses = list()
    responses.append("ABC")
    with pytest.raises(e.InvalidResponseException):
        conversions.process_single_nonpaginated_resource(responses=responses)


def test_process_single_nonpaginated_resource_receives_wrong_type():
    responses = "ABC"
    with pytest.raises(e.InvalidResponseException):
        conversions.process_single_nonpaginated_resource(responses=responses)


def test_process_multiple_nonpaginated_resource_receives_list_with_single_response_obj():
    responses = list()
    responses.append(
        httpx.Response(
            status_code=200, headers=None, request=None, json={"key": "value"}
        )
    )
    result = conversions.process_multiple_nonpaginated_resources(responses=responses)
    assert type(result) == list
    assert len(result) == 1
    assert [type(r) == dict for r in result]


def test_process_multiple_nonpaginated_resources_receives_list_with_multiple_response_obj():
    responses = list()
    [
        responses.append(
            httpx.Response(
                status_code=200, headers=None, request=None, json={"key": "value"}
            )
        )
        for _ in range(3)
    ]
    result = conversions.process_multiple_nonpaginated_resources(responses=responses)
    assert type(result) == list
    assert len(result) == 3
    assert [type(r) == dict for r in result]


def test_process_multiple_nonpaginated_resources_receives_wrong_list_type():
    responses = list()
    responses.append("ABC")
    with pytest.raises(e.InvalidResponseException):
        conversions.process_multiple_nonpaginated_resources(responses=responses)


def test_process_multiple_nonpaginated_resources_receives_wrong_type():
    responses = "ABC"
    with pytest.raises(e.InvalidResponseException):
        conversions.process_multiple_nonpaginated_resources(responses=responses)
