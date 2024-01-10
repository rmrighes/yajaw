""" Module responsible for the definition of custom exceptions."""

class ResourceUnauthorizedError(Exception):
    "Resource unauthorized"

class ResourceForbiddenError(Exception):
    "Resource forbidden"

class ResourceNotFoundError(Exception):
    "Resource not found"

class InvalidResponseError(Exception):
    "Response is not valid!"
