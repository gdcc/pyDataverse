# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
from __future__ import absolute_import
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import json_to_dict
from pyDataverse.utils import read_file_json
from pyDataverse.utils import write_file_json


"""
Data-structure to work with data and metadata of Dataverses, Datasets and
Datafiles - coming from different sources.
"""


class Dataverse(object):
    """Base class for the Dataverse model.

    * data
        * dict: dict mit key value pairs übergeben, wo key exakt das attribut ist.
        * optional: list: liste tuples (links key, rechts value) übergeben, wo key exakt das attribut ist.
    * does: set metadata functions: dicts mit key-value pairs übergeben. die keys müssen wie die metadata attribute

    """

    def __init__(self):
        """Init a `Dataverse()` class."""
        self.name = None
        self.alias = None
        self.contactEmail = []
        self.affiliation = None
        self.description = None
        self.dataverseType = None
        self.datasets = []

    def __str__(self):
        """Return name of Dataverse() class for users."""
        return 'pyDataverse Dataverse() model class.'

    def set(self, data):
        """Set attributes."""
        if isinstance(data, list):
            # TODO: prüfen, ob die struktur passt
            data = dict(data)
        elif not isinstance(data, dict):
            # TODO: Exception raisen
            print('Data was not passed in the correct data type. Dict() or '
                  'List() required.')

        for key, val in data.items():
            # TODO: prüfen, ob es sich immer um strings handelt bei den keys und values.
            if key == 'alias':
                self.alias = val
            elif key == 'name':
                self.name = val
            elif key == 'contactEmail':
                # TODO: add oder overwrite??
                if isinstance(val, list):
                    for email in val:
                        self.contactEmail.append(email)
                elif isinstance(val, str):
                    self.contactEmail.append(val)
                else:
                    # TODO: Exception
                    print('contactEmail "{}" not a list or a string. Do not'
                          ' know what to do'.format(val))
            elif key == 'affiliation':
                self.affiliation = val
            elif key == 'description':
                self.description = val
            elif key == 'dataverseType':
                self.dataverseType = val
            else:
                print('Key "{}" passed is not valid'.format(key))

    @property
    def dict(self):
        """Get Dataverse metadata as dict for Dataverse API upload.

        TODO: Validate standard

        """
        data = {}

        # prüfen, ob required attributes gesetzt sind. wenn nicht = Exception!
        if self.alias:
            data['alias'] = self.alias
        if self.name:
            data['name'] = self.name
        if self.contactEmail:
            data['dataverseContacts'] = []
            for email in self.contactEmail:
                data['dataverseContacts'].append({'contactEmail': email})
        if self.affiliation:
            data['affiliation'] = self.affiliation
        if self.description:
            data['description'] = self.description
        if self.dataverseType:
            data['dataverseType'] = self.dataverseType

        return data

    @property
    def json(self):
        """Get Dataverse metadata as json for Dataverse API upload.

        TODO: Validate standard

        Example: Default dataverse metadata json:
        {
          "name": "Scientific Research",
          "alias": "science",
          "dataverseContacts": [
            {
              "contactEmail": "pi@example.edu"
            },
            {
              "contactEmail": "student@example.edu"
            }
          ],
          "affiliation": "Scientific Research University",
          "description": "We do all the science.",
          "dataverseType": "LABORATORY"
        }

        """
        return dict_to_json(self.dict)

    def import_data(self, filename, format):
        """Import data from different sources.

        does: mappen der metadaten in die interne datenstruktur -> set()

        Example: Default dataverse metadata json:
        {
          "name": "Scientific Research",
          "alias": "science",
          "dataverseContacts": [
            {
              "contactEmail": "pi@example.edu"
            },
            {
              "contactEmail": "student@example.edu"
            }
          ],
          "affiliation": "Scientific Research University",
          "description": "We do all the science.",
          "dataverseType": "LABORATORY"
        }

        filename: string
        format: `dv_up`, `dv_down`
        return: True

        """
        if format == 'dv_up' or format == 'dv_down':
            data = read_file_json(filename)
            # TODO: welche der variablen sind den required? wie soll damit umgegangen werden?
            if 'name' in data:
                self.name = data['name']
            if 'alias' in data:
                self.alias = data['alias']
            if 'dataverseContacts' in data:
                for contact in data['dataverseContacts']:
                    for key, val in contact.items():
                        if key == 'contactEmail':
                            self.contactEmail.append(val)
            if 'affiliation' in data:
                self.affiliation = data['affiliation']
            if 'description' in data:
                self.description = data['description']
            if 'dataverseType' in data:
                self.dataverseType = data['dataverseType']
        else:
            # TODO: Exception
            print('Data-format not right')

    def export_data(self, filename, format):
        """Export data to different file-formats.

        format: `dv_up`

        """
        if format == 'dv_up':
            return write_file_json(filename, self.dict)
        else:
            # TODO: Exception
            print('Data-format not right')
