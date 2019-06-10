# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Datafile data model tests."""
import os
from pyDataverse.models import Datafile

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


class TestDatafile(object):
    """Tests for Datafile()."""

    def test_datafile_init(self):
        """Test Datafile.__init__()."""
        df = Datafile()

        assert not df.pid
        assert not df.filename
        assert not df.description
        assert not df.restrict

        df = Datafile('tests/data/datafile.txt', 'doi:10.11587/EVMUHP')

        assert df.pid == 'doi:10.11587/EVMUHP'
        assert df.filename == 'tests/data/datafile.txt'
        assert not df.description
        assert not df.restrict

    def test_datafile_set_dv_up(self, import_datafile_full_dict):
        """Test Datafile.set() with format=`dv_up`.

        Parameters
        ----------
        import_datafile_full_dict : dict
            Fixture, which returns a flat datafile dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)

        assert df.pid == 'doi:10.11587/EVMUHP'
        assert df.filename == 'tests/data/datafile.txt'
        assert df.description == 'Test datafile'
        assert not df.restrict

    def test_datafile_is_valid_valid(self, import_datafile_full_dict):
        """Test Datafile.is_valid() with valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat datafile dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)

        assert df.pid == 'doi:10.11587/EVMUHP'
        assert df.filename == 'tests/data/datafile.txt'
        assert df.description == 'Test datafile'
        assert not df.restrict
        assert df.is_valid()

    def test_datafile_is_valid_not(self, import_datafile_full_dict):
        """Test Datafile.is_valid() with non-valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat datafile dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)
        df.filename = None

        assert df.pid == 'doi:10.11587/EVMUHP'
        assert not df.filename
        assert df.description == 'Test datafile'
        assert not df.restrict
        assert not df.is_valid()

    def test_datafile_dict_dv_up_valid(self, import_datafile_full_dict):
        """Test Datafile.dict() with format=`dv_up` and valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)
        data = df.dict()

        assert df.dict('dv_up')
        assert data
        assert isinstance(data, dict)
        assert data['pid'] == 'doi:10.11587/EVMUHP'
        assert data['description'] == 'Test datafile'
        print(data)
        assert not data['restrict']

    def test_datafile_dict_all_valid(self, import_datafile_full_dict):
        """Test Datafile.dict() with format=`all` and valid data.

        Parameters
        ----------
        import_datafile_full_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)
        data = df.dict('all')

        assert data
        assert isinstance(data, dict)
        assert data['pid'] == 'doi:10.11587/EVMUHP'
        assert data['filename'] == 'tests/data/datafile.txt'
        assert data['description'] == 'Test datafile'
        assert not data['restrict']

    def test_datafile_dict_format_wrong(self, import_datafile_full_dict):
        """Test Datafile.dict() with non-valid format.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)
        data = df.dict('wrong')

        assert not data

    def test_datafile_dict_dv_up_valid_not(self, import_datafile_min_dict):
        """Test Datafile.dict() with format=`dv_up` and non-valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_min_dict
        df = Datafile()
        df.set(data)
        df.pid = None

        assert not df.is_valid()
        assert df.filename == 'tests/data/datafile.txt'

    def test_datafile_json_dv_up_valid(self, import_datafile_min_dict):
        """Test Datafile.json() with format=`dv_up` and valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_min_dict
        df = Datafile()
        df.set(data)
        data = df.json()

        assert data
        assert isinstance(data, str)

    def test_datafile_json_dv_up_valid_not(self, import_datafile_min_dict):
        """Test Datafile.json() with format=`dv_up` and non-valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_min_dict
        df = Datafile()
        df.set(data)
        df.filename = None

        assert not df.is_valid()
        print(df.json('dv_up'))
        assert not df.json('dv_up')

    def test_datafile_json_all_valid(self, import_datafile_full_dict):
        """Test Datafile.json() with format=`all` and valid data.

        Parameters
        ----------
        import_datafile_full_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_full_dict
        df = Datafile()
        df.set(data)
        data = df.json('all')

        assert data
        assert isinstance(data, str)

    def test_datafile_json_format_wrong_valid(self, import_datafile_min_dict):
        """Test Datafile.json() with non-valid format and valid data.

        Parameters
        ----------
        import_datafile_min_dict : dict
            Fixture, which returns a flat dataset dict().

        """
        data = import_datafile_min_dict
        df = Datafile()
        df.set(data)
        data = df.json('wrong')

        assert not data
