"""
Pre-publish script for pyDataverse package.

This script performs version validation and package name modification before publishing
to TestPyPI. It ensures that the version tag matches across different configuration files
and renames the package for TestPyPI compatibility.

The script performs the following operations:
1. Extracts version tag from GitHub environment variable
2. Validates version consistency across pyproject.toml and __init__.py
3. Modifies package name for TestPyPI publication
"""

import os
import toml
import pyDataverse


def get_version_from_git_ref():
    """
    Extract version tag from the GitHub reference name.

    Returns:
        str: Version string with 'v' prefix removed if present

    Raises:
        ValueError: If VERSION_TAG environment variable is not set
    """
    version_tag = os.getenv("VERSION_TAG", None)

    if version_tag is None:
        raise ValueError("Version tag is not set")
    else:
        # Remove 'v' prefix if present (e.g., "v0.3.5" -> "0.3.5")
        version_tag = version_tag.replace("v", "")

    return version_tag


def validate_version_consistency(version_tag):
    """
    Validate that the version tag matches the versions specified in configuration files.

    Args:
        version_tag (str): The version tag to validate against

    Raises:
        AssertionError: If versions don't match between files
    """
    # Load and check version in pyproject.toml
    pyproject = toml.load("pyproject.toml")
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    assert version_tag == pyproject_version, (
        f"Version tag does not match package version in pyproject.toml: "
        f"{version_tag} != {pyproject_version}"
    )

    # Check version in __init__.py
    init_version = pyDataverse.__version__
    assert version_tag == init_version, (
        f"Version tag does not match package version in __init__.py: "
        f"{version_tag} != {init_version}"
    )

    return pyproject


def modify_package_name_for_testpypi(pyproject):
    """
    Modify the package name for TestPyPI publication.

    Since we don't have access to the original 'pyDataverse' package name on TestPyPI,
    we rename it to 'pyDataverse-test' to avoid conflicts.

    Args:
        pyproject (dict): The loaded pyproject.toml configuration
    """
    # For TestPyPI, we will rename the package to pyDataverse-test
    # because we do not have access to the original package name
    pyproject["tool"]["poetry"]["name"] = "pyDataverse-test"

    # Write the modified configuration back to pyproject.toml
    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)


def main():
    """
    Main execution function that orchestrates the pre-publish process.
    """
    # Get the version tag from the current branch
    version_tag = get_version_from_git_ref()

    # Validate version consistency across configuration files
    pyproject = validate_version_consistency(version_tag)

    # Modify package name for TestPyPI compatibility
    modify_package_name_for_testpypi(pyproject)


if __name__ == "__main__":
    main()
