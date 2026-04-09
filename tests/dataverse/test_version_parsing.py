"""Unit tests for Dataverse version parsing."""

import pytest

from pyDataverse.dataverse.dataverse import _extract_major_version


@pytest.mark.parametrize(
    "version_string, expected_major",
    [
        ("6.10", 6),
        ("v6.10.1", 6),
        ("6.10.1-SNAPSHOT", 6),
        ("6.10 bugfixes", 6),
        ("  7.2 custom-build  ", 7),
    ],
)
def test_extract_major_version_accepts_known_formats(
    version_string: str, expected_major: int
) -> None:
    """It parses major versions from canonical and descriptor-suffixed strings."""
    assert _extract_major_version(version_string) == expected_major


@pytest.mark.parametrize("version_string", ["", "bugfixes 6.10", "release-v6.10"])
def test_extract_major_version_rejects_invalid_prefix(version_string: str) -> None:
    """It fails if the version string does not start with a version number."""
    with pytest.raises(ValueError, match="Unable to parse version string"):
        _extract_major_version(version_string)
