"""
exceptions.py — Structured exception hierarchy for Dataverse API client

These exceptions provide clear, predictable error types for callers of the
DataverseClient and its endpoint modules. They map directly to common HTTP
error classes and Dataverse-specific failure modes.
"""


class DataverseError(Exception):
    """
    Base class for all Dataverse-related errors.

    Any unexpected or unclassified error raised by the client should inherit
    from this type.
    """

    pass


class AuthenticationError(DataverseError):
    """
    Raised when authentication fails (HTTP 401/403).

    Typically caused by:
    - Missing or invalid API token
    - Insufficient permissions for the requested operation
    """

    pass


class NotFoundError(DataverseError):
    """
    Raised when a requested resource does not exist (HTTP 404).

    Examples:
    - Dataset not found
    - File ID does not exist
    - Dataverse alias is invalid
    """

    pass


class ValidationError(DataverseError):
    """
    Raised when the server rejects the request due to invalid input (HTTP 400).

    Examples:
    - Invalid metadata structure
    - Missing required fields
    - Unsupported parameters
    """

    pass


class ServerError(DataverseError):
    """
    Raised when the Dataverse server encounters an internal error (HTTP 5xx).

    Examples:
    - Dataverse backend failure
    - Solr or database outage
    - Temporary server overload
    """

    pass


class RateLimitError(DataverseError):
    """
    Raised when the server rate-limits the client (HTTP 429).

    Not all Dataverse installations enforce rate limits, but this exception
    is included for completeness and future-proofing.
    """

    pass
