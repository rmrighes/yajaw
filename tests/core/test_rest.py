import pytest
from yajaw.core.rest import _retry_response_error_detected, log_and_raise_request_issue, _retry_request, _log_attempt_info, _send_request
from yajaw.configuration import YajawConfig
from yajaw.core.exceptions import InvalidResponseError, ResourceUnauthorizedError, ResourceForbiddenError, ResourceMethodNotAllowedError, ResourceNotFoundError
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
from http import HTTPStatus
import asyncio
import secrets

@pytest.mark.asyncio
async def test_retry_response_error_detected():
    # Test case where result is not an instance of httpx.Response
    with pytest.raises(InvalidResponseError):
        _retry_response_error_detected("not_a_response")

    # Test case where result has status code UNAUTHORIZED
    result = MagicMock(spec=httpx.Response, status_code=HTTPStatus.UNAUTHORIZED)
    with pytest.raises(ResourceUnauthorizedError):
        _retry_response_error_detected(result)

    # Test case where result has status code FORBIDDEN
    result = MagicMock(spec=httpx.Response, status_code=HTTPStatus.FORBIDDEN)
    with pytest.raises(ResourceForbiddenError):
        _retry_response_error_detected(result)

    # Test case where result has status code METHOD_NOT_ALLOWED
    result = MagicMock(spec=httpx.Response, status_code=HTTPStatus.METHOD_NOT_ALLOWED)
    with pytest.raises(ResourceMethodNotAllowedError):
        _retry_response_error_detected(result)

    # Test case where result has status code NOT_FOUND
    result = MagicMock(spec=httpx.Response, status_code=HTTPStatus.NOT_FOUND)
    with pytest.raises(ResourceNotFoundError):
        _retry_response_error_detected(result)

    # Test case where result has a different status code
    result = MagicMock(spec=httpx.Response, status_code=HTTPStatus.OK)
    assert not _retry_response_error_detected(result)

@pytest.mark.asyncio
async def test_retry_request():
    jira_info = MagicMock()
    client = MagicMock(spec=httpx.AsyncClient)
    YajawConfig.TRIES = 3
    YajawConfig.DELAY = 1

    # Mock _send_request function
    with patch('yajaw.core.rest._send_request', return_value=MagicMock("not a response object")) as mock_send_request:
        with pytest.raises(InvalidResponseError):
            await _retry_request(jira_info, client)

    mock_send_request.assert_called_with(jira=jira_info, client=client)