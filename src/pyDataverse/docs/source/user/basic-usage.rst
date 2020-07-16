.. _user_basic-usage:

Basic Usage
=================

Requirements
-----------------------------

pyDataverse installed LINK

.. warning::
  Do not execute the examples code on your production instance!


Get started!
-----------------------------

Init Dataset

>>> from pyDataverse.models import Dataset
>>> ds = Dataset()

Import metadata from JSON file (format=dataverse_upload)

>>> from pyDataverse.utils import read_file
>>> json_filename = 'tests/data/dataset_upload_min_tutorial_mass-migration.json'
>>> ds.from_json(read_file(json_filename))
>>> ds.get()
{'citation_displayName': 'Citation Metadata', 'title': 'Youth in Austria 2005', 'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1'}], 'datasetContact': [{'datasetContactEmail': 'ContactEmail1@mailinator.com', 'datasetContactName': 'LastContact1, FirstContact1'}], 'dsDescription': [{'dsDescriptionValue': 'DescriptionText'}], 'subject': ['Medicine, Health and Life Sciences']}

Manipulate Dataset metadata

>>> ds.get()['title']
Youth in Austria 2005
>>> ds.set({'title': 'Youth from Austria 2005'})
>>> ds.get()['title']
Youth from Austria 2005

Export metadata as JSON string for API upload (format=dataverse_upload)

>>> ds_json = ds.to_json()

Init Native API

>>> from pyDataverse.api import NativeApi
>>> base_url = 'YOUR_BASE_URL'  # e.g. 'https://demo.dataverse.org'
>>> api_token = 'YOUR_API_TOKEN'  # @USERNAME
>>> api = NativeApi(base_url, api_token)

Upload Dataset via API

>>> dv_parent_alias = 'DATAVERSE_PARENT_ALIAS'  # e.g. 'public'
>>> resp = api.create_dataset(dv_parent_alias, ds_json)
Dataset with pid 'doi:10.5072/FK2/UTGITX' created.
>>> resp.json()
{'status': 'OK', 'data': {'id': 251, 'persistentId': 'doi:10.5072/FK2/UTGITX'}}
>>> ds_pid = resp.json()['data']['persistentId']

Init Datafile

>>> from pyDataverse.models import Datafile
>>> df = Datafile()

Set Datafile metadata

>>> df_filename = 'tests/data/datafile.txt'
>>> df.set({'pid': ds_pid, 'filename': df_filename})
>>> df.get()
{'pid': 'doi:10.5072/FK2/UTGITX', 'filename': 'tests/data/datafile.txt'}

Upload Datafile via API

>>> resp = api.upload_datafile(ds_pid, df_filename, json_str=df.to_json())
>>> resp.status_code
200
