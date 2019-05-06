from __future__ import absolute_import


class DataverseError(Exception):
    """Base exception class for Dataverse-related error."""

    pass


class DataverseApiError(DataverseError):
    """Base exception class for Dataverse-related API error."""

    pass


class OperationFailedError(DataverseApiError):
    """Raised when an operation fails for an unknown reason."""

    pass


class UnauthorizedError(OperationFailedError):
    """Raised if a user provides invalid credentials."""

    pass


class ConnectionError(OperationFailedError):
    """Raised when connection fails for an unknown reason."""

    pass


class DataverseNotFoundError(OperationFailedError):
    """Raised when a Dataverse cannot be found."""

    pass
