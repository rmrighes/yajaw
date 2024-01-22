""" Module responsible for the definition of custom exceptions."""


class YajawError(Exception):
    "Base class for yajaw errors"


class InvalidResponseError(YajawError):
    "Response is not valid!"


class HttpClientError(YajawError):
    "Returned HTTP Status Code is 4xx"


class HttpServerError(YajawError):
    "Returned HTTP Status Code is 5xx"


class ResourceUnauthorizedError(HttpClientError):
    "Resource unauthorized"


class ResourceForbiddenError(HttpClientError):
    "Resource forbidden"


class ResourceNotFoundError(HttpClientError):
    "Resource not found"


class ResourceMethodNotAllowedError(HttpClientError):
    "Resource does not support method"
