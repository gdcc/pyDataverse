from __future__ import absolute_import


class DataverseError(Exception):
    """Base exception class for Dataverse-related error."""

    pass


class DataverseApiError(DataverseError):
    """Base exception class for Dataverse-related api error."""

    pass


class OperationFailedError(DataverseApiError):
    """Raised when an operation fails for an unknown reason."""

    pass


class ApiUrlError(DataverseApiError):
    """Raised when the request url is not valid."""

    pass


class ApiResponseError(DataverseApiError):
    """Raised when the requests response fails."""

    pass


class ApiAuthorizationError(OperationFailedError):
    """Raised if a user provides invalid credentials."""

    pass


class DataverseNotFoundError(OperationFailedError):
    """Raised when a Dataverse cannot be found."""

    pass
