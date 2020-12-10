"""Dataverse data model tests."""
from pyDataverse.models import DVObject


class TestDVObject(object):
    """Tests for :class:DVObject()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        obj = DVObject()

        assert not hasattr(obj, "default_json_format")
        assert not hasattr(obj, "allowed_json_formats")
        assert not hasattr(obj, "default_json_schema_filename")
        assert not hasattr(obj, "json_dataverse_upload_attr")
