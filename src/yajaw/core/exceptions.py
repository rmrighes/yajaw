class ResourceNotFoundException(Exception):
    "Resource not found!"

class ResourceNotAuthorizedException(Exception):
    "Resource not authorized!"

class InvalidResponseException(Exception):
    "Response is not valid!"
