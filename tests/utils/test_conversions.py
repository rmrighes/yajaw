"""Module responsonsible for testing yajaw.util.conversions module."""
import httpx
import pytest

from yajaw.core import exceptions as e
from yajaw.utils import conversions


def test_validate_responses_attribute_receives_list_of_response_objs():
    """Test validate_responses_attribute() with a list of httpx.Response
    objects.
    """
    responses = [
        httpx.Response(status_code=200, headers=None, request=None, json=None)
        for _ in range(3)
    ]
    assert conversions.validate_responses_attribute(responses=responses) is None


def test_validate_responses_attribute_receives_not_list():
    """Test validate_responses_attribute() with something other than a list
    of httpx.Response objects.
    """
    responses = "String"
    with pytest.raises(e.InvalidResponseError):
        conversions.validate_responses_attribute(responses=responses)


def test_validate_responses_attribute_receives_empty_list():
    """Test validate_responses_attribute() with empty list."""
    responses = []
    with pytest.raises(e.InvalidResponseError):
        conversions.validate_responses_attribute(responses=responses)


def test_validate_responses_attribute_receives_wrong_list_type():
    """Test validate_responses_attribute() with a list of something other
    than httpx.Response objects.
    """
    responses = ["First", "Second", "Third"]
    with pytest.raises(e.InvalidResponseError):
        conversions.validate_responses_attribute(responses=responses)


def test_validate_responses_attribute_receives_list_both_valid_invalid():
    """Test validate_responses_attribute() with a mixed list of
    httpx.Response objects and other types.
    """
    responses = [
        httpx.Response(status_code=200, headers=None, request=None, json=None)
        for _ in range(3)
    ]
    responses.append("String")
    with pytest.raises(e.InvalidResponseError):
        conversions.validate_responses_attribute(responses=responses)


def test_process_single_nonpaginated_resource_receives_list_with_single_response_obj():
    """Test process_single_nonpaginated_resource() with a httpx.Response
    object.
    """
    responses = []
    responses.append(
        httpx.Response(
            status_code=200, headers=None, request=None, json={"key": "value"}
        )
    )
    result = conversions.process_single_nonpaginated_resource(responses=responses)
    assert isinstance(result, dict)
    assert result["key"] == "value"


def test_process_single_nonpaginated_resource_receives_list_with_multiple_response_obj():
    """Test process_single_nonpaginated_resource() with a list of
    httpx.Response objects.
    """
    responses = [
        httpx.Response(
            status_code=200, headers=None, request=None, json={"key": "value"}
        )
        for _ in range(3)
    ]
    with pytest.raises(e.InvalidResponseError):
        conversions.process_single_nonpaginated_resource(responses=responses)


def test_process_single_nonpaginated_resource_receives_wrong_list_type():
    """Test process_single_nonpaginated_resource() with a list of something
    other than httpx.Response objects.
    """
    responses = []
    responses.append("ABC")
    with pytest.raises(e.InvalidResponseError):
        conversions.process_single_nonpaginated_resource(responses=responses)


def test_process_single_nonpaginated_resource_receives_wrong_type():
    """Test process_single_nonpaginated_resource() with something other than
    a list of httpx.Response objects.
    """
    responses = "ABC"
    with pytest.raises(e.InvalidResponseError):
        conversions.process_single_nonpaginated_resource(responses=responses)


def test_process_multiple_nonpaginated_resource_receives_list_with_single_response_obj():
    """Test process_multiple_nonpaginated_resource() with a list having a
    single httpx.Response object.
    """
    responses = []
    responses.append(
        httpx.Response(
            status_code=200, headers=None, request=None, json={"key": "value"}
        )
    )
    result = conversions.process_multiple_nonpaginated_resources(responses=responses)
    assert isinstance(result, list)
    assert len(result) == 1
    assert [isinstance(r, dict) for r in result]


def test_process_multiple_nonpaginated_resources_receives_list_with_multiple_response_obj():
    """Test process_multiple_nonpaginated_resource() with a list of
    httpx.Response objects.
    """
    responses = [
        httpx.Response(
            status_code=200, headers=None, request=None, json={"key": "value"}
        )
        for _ in range(3)
    ]
    result = conversions.process_multiple_nonpaginated_resources(responses=responses)
    assert isinstance(result, list)
    assert len(result) == 3
    assert [isinstance(r, dict) for r in result]


def test_process_multiple_nonpaginated_resources_receives_wrong_list_type():
    """Test process_multiple_nonpaginated_resource() with a list of something
    other than httpx.Response objects.
    """
    responses = []
    responses.append("ABC")
    with pytest.raises(e.InvalidResponseError):
        conversions.process_multiple_nonpaginated_resources(responses=responses)


def test_process_multiple_nonpaginated_resources_receives_wrong_type():
    """Test process_multiple_nonpaginated_resource() with something other than
    a list of httpx.Response objects.
    """
    responses = "ABC"
    with pytest.raises(e.InvalidResponseError):
        conversions.process_multiple_nonpaginated_resources(responses=responses)
