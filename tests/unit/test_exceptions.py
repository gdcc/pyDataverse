import pytest

from pyDataverse.api.exceptions import (
    AuthenticationError,
    DataverseError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

# ----------------------------------------------------------------------
# Basic instantiation
# ----------------------------------------------------------------------


def test_exceptions_can_be_instantiated():
    assert DataverseError("msg")
    assert AuthenticationError("msg")
    assert NotFoundError("msg")
    assert ValidationError("msg")
    assert ServerError("msg")
    assert RateLimitError("msg")


# ----------------------------------------------------------------------
# Inheritance relationships
# ----------------------------------------------------------------------


def test_all_exceptions_inherit_from_dataverse_error():
    assert issubclass(AuthenticationError, DataverseError)
    assert issubclass(NotFoundError, DataverseError)
    assert issubclass(ValidationError, DataverseError)
    assert issubclass(ServerError, DataverseError)
    assert issubclass(RateLimitError, DataverseError)


def test_dataverse_error_is_base_exception():
    assert issubclass(DataverseError, Exception)


# ----------------------------------------------------------------------
# Raising and catching behavior
# ----------------------------------------------------------------------


def test_specific_exceptions_can_be_caught():
    with pytest.raises(AuthenticationError):
        raise AuthenticationError("auth failed")

    with pytest.raises(NotFoundError):
        raise NotFoundError("missing")

    with pytest.raises(ValidationError):
        raise ValidationError("bad input")

    with pytest.raises(ServerError):
        raise ServerError("server exploded")

    with pytest.raises(RateLimitError):
        raise RateLimitError("too many requests")


def test_catching_as_base_class():
    with pytest.raises(DataverseError):
        raise NotFoundError("missing dataset")

    with pytest.raises(DataverseError):
        raise ServerError("boom")

    with pytest.raises(DataverseError):
        raise RateLimitError("slow down")


def test_catching_as_python_exception():
    with pytest.raises(Exception):
        raise DataverseError("generic")
