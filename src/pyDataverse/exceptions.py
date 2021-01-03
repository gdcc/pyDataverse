"""Find out more at https://github.com/GDCC/pyDataverse."""


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


class DataverseNotEmptyError(OperationFailedError):
    """Raised when a Dataverse has accessioned Datasets."""

    pass


class DataverseNotFoundError(OperationFailedError):
    """Raised when a Dataverse cannot be found."""

    pass


class DatasetNotFoundError(OperationFailedError):
    """Raised when a Dataset cannot be found."""

    pass


class DatafileNotFoundError(OperationFailedError):
    """Raised when a Datafile cannot be found."""

    pass
