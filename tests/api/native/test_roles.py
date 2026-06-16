"""Tests for the Roles functionality in NativeApi.

This module contains test functions for role-related operations
including retrieving, creating, showing, and deleting roles.
"""

import random
from string import ascii_letters

from pyDataverse.api.native import NativeApi
from pyDataverse.models import collection
from tests.conftest import Credentials


class TestRoles:
    """Test suite for Roles functionality.

    Tests cover role management including retrieving roles, creating custom roles,
    viewing role details, and deleting roles within a Dataverse collection.
    """

    def test_get_dataverse_roles(
        self,
        native_api: NativeApi,
    ):
        """Test retrieving all roles defined in a dataverse.

        Verifies that get_dataverse_roles() returns a list of all roles available
        in a dataverse, including default roles like "admin" and any custom roles.
        """
        roles = native_api.get_dataverse_roles("root")

        assert len(roles) > 0, "Roles should be more than one"
        assert roles[0].alias == "admin", "Role should be admin"
        assert roles[0].name == "Admin", "Role should be Admin"

    def test_create_delete_role(
        self,
        native_api: NativeApi,
    ):
        """Test creating and deleting a role in a dataverse.

        Verifies that a custom role can be created with specific permissions,
        retrieved from the role list, and then deleted, ensuring proper role
        lifecycle management.
        """

        role_alias = f"role{''.join(random.choices(ascii_letters, k=10))}".lower()
        role = native_api.create_role(
            dataverse_id="root",
            role=collection.Role(
                alias=role_alias,
                name=f"TestRole {role_alias}",
                description="Test Role Description",
                permissions=["AddDataset"],
            ),
        )

        # Check if the role was created
        roles = native_api.get_dataverse_roles("root")
        role = next((r for r in roles if r.alias == role_alias), None)

        assert role is not None, "Role should be created"
        assert role.id is not None, "Role ID should be not None"

        # Delete the role
        native_api.delete_role(role.id)
        roles = native_api.get_dataverse_roles("root")

        assert not any(r.alias == "test" for r in roles), "Role should be deleted"

    def test_show_role(self, native_api: NativeApi, credentials: Credentials):
        """Test retrieving detailed information for a specific role by ID.

        Verifies that show_role() returns complete role information including
        permissions, description, and other role properties for a given role ID.
        """
        admin_role = next(
            (r for r in native_api.get_dataverse_roles("root") if r.alias == "admin"),
            None,
        )
        assert admin_role is not None, "Admin role should be found"
        assert admin_role.id is not None, "Admin role ID should be not None"

        role = native_api.show_role(admin_role.id)
        assert role is not None, "Role should be retrieved"
