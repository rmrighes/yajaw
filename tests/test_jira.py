from unittest.mock import patch

import httpx
import pytest

from yajaw.core import exceptions as e
from yajaw.jira import *

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
    return httpx.Response(
        status_code=200, headers=None, request=None, json={"key": "VALID"}
    )


def fetch_single_mock_not_found_issue() -> httpx.Response:
    return httpx.Response(status_code=404, headers=None, request=None, json={})


@patch("httpx.AsyncClient.request")
def test_fetch_single_valid_issue(mock_rest_request):
    mock_response = fetch_single_mock_valid_issue()
    mock_rest_request.return_value = mock_response
    response = fetch_project("VALID")
    assert type(response) == dict
    assert response["key"] == "VALID"


@patch("httpx.AsyncClient.request")
def test_fetch_single_not_found_issue(mock_rest_request):
    mock_response = fetch_single_mock_not_found_issue()
    mock_rest_request.return_value = mock_response
    with pytest.raises(e.ResourceNotFoundException):
        fetch_project("INVALID")
