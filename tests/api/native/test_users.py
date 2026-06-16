"""Tests for the Users functionality in NativeApi.

This module contains test functions for user-related operations
including API token management and user information retrieval.
"""

from pyDataverse.api.native import NativeApi
from tests.conftest import Credentials


class TestUsers:
    """Test suite for Users functionality.
    
    Tests cover user information retrieval and API token management
    for the currently authenticated user.
    """

    def test_get_user(self, native_api: NativeApi, credentials: Credentials):
        """Test retrieving details of the currently authenticated user.
        
        Verifies that get_user() returns user information including ID, display name,
        and email for the user associated with the current API token.
        """
        user = native_api.get_user()
        assert user is not None, "User should be found"
        assert user.id is not None, "User ID should be not None"
        assert user.display_name is not None, "User display name should be not None"
        assert user.email is not None, "User email should be not None"

    def test_get_user_api_token_expiration_date(
        self, native_api: NativeApi, credentials: Credentials
    ):
        """Test retrieving the expiration date of the current user's API token.
        
        Verifies that get_user_api_token_expiration_date() returns information
        about when the current API token will expire, allowing users to manage
        token lifecycle.
        """
        expiration = native_api.get_user_api_token_expiration_date()
        assert expiration is not None, "Expiration should be found"
        assert expiration.message is not None, "Expiration message should be not None"
