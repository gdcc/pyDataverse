# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse data model tests."""
import json
import os
from pyDataverse.models import DVObject
import pytest


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDVObject(object):
    """Tests for :class:DVObject()."""

    def test_dataverse_init(self):
        """Test Dataverse.__init__()."""
        obj = DVObject()
        assert obj.default_validate_format == 'dataverse_upload'
        assert obj.attr_dv_up_values == None
        assert str(obj) == 'pyDataverse DVObject() model class.'
