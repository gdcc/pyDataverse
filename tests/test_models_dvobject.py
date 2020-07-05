# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import json
import os

import pytest
from pyDataverse.models import DVObject

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDVObject(object):
    """Tests for :class:DVObject()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        obj = DVObject()

        assert not hasattr(obj, 'default_json_format')
        assert not hasattr(obj, 'allowed_json_formats')
        assert not hasattr(obj, 'default_json_schema_filename')
        assert not hasattr(obj, 'json_dataverse_upload_attr')
