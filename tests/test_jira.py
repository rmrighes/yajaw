"""Module responsonsible for testing yajaw.jira module."""
from unittest.mock import patch

import httpx
import pytest

from yajaw import jira
from yajaw.core import exceptions as e

#########
# MOCK!!!
#########

# Reference for httpx.Response:
# https://github.com/encode/httpx/blob/master/httpx/_models.py

# status_code: int,
# headers: typing.Optional[HeaderTypes] = None,
# content: typing.Optional[ResponseContent] = None,
# text: typing.Optional[str] = None,
# html: typing.Optional[str] = None,
# json: typing.Any = None,
# stream: typing.Union[SyncByteStream, AsyncByteStream, None] = None,
# request: typing.Optional[Request] = None,
# extensions: typing.Optional[ResponseExtensions] = None,
# history: typing.Optional[typing.List["Response"]] = None,
# default_encoding: typing.Union[str, typing.Callable[[bytes], str]] = "utf-8",


def fetch_single_mock_valid_issue() -> httpx.Response:
    """Auxiliry function to generate a valid issue as httpx.Response to be
    used in different tests.
    """
    return httpx.Response(
        status_code=200,
        headers=None,
        request=httpx.Request("GET", "https://example.org"),
        json={"key": "VALID"},
    )


def fetch_single_mock_server_not_found() -> httpx.Response:
    """Auxiliary function to generate a server not found httpx.Response
    to be used in different tests.
    """
    return httpx.Response(status_code=503, headers=None, request=None, json={})


def fetch_single_mock_not_found_issue() -> httpx.Response:
    """Auxiliary function to generate a resource not found httpx.Response
    to be used in different tests.
    """
    return httpx.Response(status_code=404, headers=None, request=None, json={})


@patch("httpx.AsyncClient.request")
def test_fetch_single_valid_issue(mock_rest_request):
    """Test fetch_project() with a single valid issue."""
    mock_response = fetch_single_mock_valid_issue()
    mock_rest_request.return_value = mock_response
    response = jira.fetch_project("VALID")
    assert isinstance(response, dict)
    assert response["key"] == "VALID"


@patch("httpx.AsyncClient.request")
@patch("asyncio.sleep")
def test_fetch_single_issue_with_server_not_found(mock_rest_request, mock_sleep):
    """Test fetch_project() with an invalid response."""
    mock_value = fetch_single_mock_server_not_found()
    mock_rest_request.return_value = mock_value
    mock_sleep.return_value = None
    with pytest.raises(e.YajawError):
        jira.fetch_project("INVALID-KEY")
