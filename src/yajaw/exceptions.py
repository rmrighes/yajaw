"""
Module responsible for the definition of yajaw exceptions.
"""


class YajawError(Exception):
    """
    Base class for yajaw errors.
    Error is derived from super class Exception.
    """


class InvalidResponseError(YajawError):
    """
    Response received is not valid. It is usually raised from
    underlying problems, such as runtime errors in HTTP requests,
    or processing the received results.
    Error is derived from super class YajawError.
    """


class HttpClientError(YajawError):
    """
    Base class for errors associated with a HTTP Status Code 4xx.
    Error is derived from super class YajawError.
    """


class HttpServerError(YajawError):
    """
    Base class for errors associated with a HTTP Status Code 5xx.
    Error is derived from super class HttpClientError.
    """


class ResourceUnauthorizedError(HttpClientError):
    """
    Authenticated user is unauthorized from access the resource.
    Error is derived from super class HttpClientError.
    """


class ResourceForbiddenError(HttpClientError):
    """
    Authenticated user is forbidden from access the resource.
    Error is derived from super class HttpClientError.
    """


class ResourceNotFoundError(HttpClientError):
    """
    Requested resource could not be found as informed.
    Error is derived from super class HttpClientError.
    """


class ResourceMethodNotAllowedError(HttpClientError):
    """
    Requested resource does not support the informed HTTP method.
    Low level error for internal modules use.
    Error is derived from super class HttpClientError.
    """
