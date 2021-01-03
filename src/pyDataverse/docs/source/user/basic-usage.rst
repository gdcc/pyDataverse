.. _user_basic-usage:

Basic Usage
=================

To get started, we will import metadata from JSON-files, create data objects
- one Dataverse, Dataset and Datafile - from it and clean up at the end.

The data for this tutorial can be found inside ``tests/data/basic-usage/``.

.. include:: ../snippets/warning_production.rst

In addition to this tutorial, you can find specific examples at
:ref:`User Guide - Use-Cases <user_use-cases>`.


Requirements
-----------------------------

- pyDataverse (see :ref:`install <user_installation>`)


Tutorial
-----------------------------


Initialize Native API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, create a :class:`NativeApi <pyDataverse.api.NativeApi>` instance to use it
later for the data creations. Replace {BASE_URL} and {API_TOKEN} with
your instance specific values.

>>> from pyDataverse.api import NativeApi
>>> base_url = "{BASE_URL}"  # e.g. https://demo.dataverse.org
>>> api_token = "{API_TOKEN}"  # @USERNAME e. g. dataverseAdmin
>>> api = NativeApi(base_url, api_token)

Check, if our API connection works and get the version of the Dataverse instance
(:meth:`get_info_version() <pyDataverse.api.get_info_version>`).

>>> resp = api.get_info_version()

All API requests return a :class:`requests.Response <requests.Response>` object, which
can then be used (e. g. :meth:`json() <requests.Response.json>`).

>>> resp.json()
{'status': 'OK', 'data': {'version': '{DATAVERSE_VERSION', 'build': '{DATAVERSE_BUILD}'}}

>>> resp.status_code
200


Create Dataverse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The top-level data type is a Dataverse, so we will start with it.

First, instantiate a :class:`Dataverse <pyDataverse.models.Dataverse>`
object and import the metadata from a JSON-file
(:meth:`from_json() <pyDataverse.models.Dataverse.from_json>`).

>>> from pyDataverse.models import Dataverse
>>> from pyDataverse.utils import read_file
>>> dv = Dataverse()
>>> dv_filename = "tests/data/user-guide/dataverse.json"
>>> dv.from_json(read_file(dv_filename))

:meth:`get() <pyDataverse.models.Dataverse.get>` outputs the metadata imported as
a :class:`dict`.

>>> dv.get()
{'alias': 'pyDataverse_user-guide', 'name': 'pyDataverse - User Guide', 'dataverseContacts': [{'contactEmail': 'info@aussda.at'}]}
>>> type(dv.get())
<class 'dict'>

You also can output the metadata with :meth:`json() <pyDataverse.models.Dataverse.json>`
as JSON, which defaults to the needed format for the Dataverse API upload
(``data_format="dataverse_upload"``).

>>> dv.json()
'{\n  "alias": "pyDataverse_user-guide",\n  "dataverseContacts": [\n    {\n      "contactEmail": "info@aussda.at"\n    }\n  ],\n  "name": "pyDataverse - User Guide"\n}'
>>> type(dv.json())
<class 'str'>

Then use :meth:`create_dataverse() <pyDataverse.api.create_dataverse>`, to
upload the Dataverse metadata to your Dataverse instance and create a
Dataverse Draft object. You have to pass the parent Dataverse, and pass the
metadata as JSON.

>>> resp = api.create_dataverse(":root", dv.json())
Dataverse pyDataverse_user-guide created.

Last, publish the Dataverse Draft with
:meth:`publish_dataverse() <pyDataverse.api.publish_dataverse>`.

>>> resp = api.publish_dataverse("pyDataverse_user-guide")
Dataverse pyDataverse_user-guide published.

This is it! We created our first Dataverse data object with the help of the
Dataverse API and pyDataverse.

We can now retrieve it with (:meth:`get_dataverse() <pyDataverse.api.get_dataverse>`).

>>> resp = api.get_dataverse("pyDataverse_user-guide")
>>> resp.json()
{'status': 'OK', 'data': {'id': {DATAVERSE_ID}, 'alias': 'pyDataverse_user-guide', 'name': 'pyDataverse - User Guide', 'dataverseContacts': [{'displayOrder': 0, 'contactEmail': 'info@aussda.at'}], 'permissionRoot': True, 'dataverseType': 'UNCATEGORIZED', 'ownerId': 1, 'creationDate': '{TIMESTAMP}'}}


Create Dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instantiate a :class:`Dataset <pyDataverse.models.Dataverse>`.

>>> from pyDataverse.models import Dataset
>>> ds = Dataset()

Same as for the Dataverse, use :meth:`from_json() <pyDataverse.models.Dataset.from_json>` to import
the metadata from your JSON-file.

>>> ds_filename = "tests/data/user-guide/dataset.json"
>>> ds.from_json(read_file(ds_filename))

As you can see, the models are pretty similiar. You can also use :meth:`get() <pyDataverse.models.Dataset.get>`
to output your metadata.

>>> ds.get()
{'citation_displayName': 'Citation Metadata', 'title': 'Youth in Austria 2005', 'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1'}], 'datasetContact': [{'datasetContactEmail': 'ContactEmail1@mailinator.com', 'datasetContactName': 'LastContact1, FirstContact1'}], 'dsDescription': [{'dsDescriptionValue': 'DescriptionText'}], 'subject': ['Medicine, Health and Life Sciences']}

This time, we want to manipulate the object a bit, before we upload it.
Simply use :meth:`set() <pyDataverse.models.Dataset.set>` for this. 
You can pass any attribute you want as key-value pairs in a :class:`dict`.

>>> ds.get()["title"]
Youth in Austria 2005
>>> ds.set({"title": "Youth from Austria 2005"})
>>> ds.get()["title"]
Youth from Austria 2005

To upload a Dataset with :meth:`create_dataset() <pyDataverse.api.create_dataset>`,
you have to tell to which Dataverse the Dataset gets attached to and pass the
metadata as a JSON string (:meth:`json() <pyDataverse.models.Dataset.json>`).

>>> resp = api.create_dataset("pyDataverse_user-guide", ds.json())
Dataset with pid '{DOI}' created.
>>> resp.json()
{'status': 'OK', 'data': {'id': {DATASET_ID}, 'persistentId': '{DOI}'}}

To use the Dataset later on, you have to save the created PID.

>>> ds_pid = resp.json()["data"]["persistentId"]

You can now create a private Dataset URL with 
:meth:`create_dataset_private_url() <pyDataverse.api.create_dataset_private_url>`.

>>> resp = api.create_dataset_private_url(ds_pid)
>>> resp.json()
Dataset private URL created: {BASE_URL}/privateurl.xhtml?token=24cdaf83-7c3c-4123-bd10-482e6b7d6e15

Finally, to make the Dataset public, publish the Draft with
:meth:`publish_dataset() <pyDataverse.api.publish_dataset>`.
Set the ``release_type="major"`` (defaults to ``minor``), to create version 1.0.

>>> resp = api.publish_dataset(ds_pid, release_type="major")
Dataset {DOI} published.


Upload Datafile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Last, we upload a :class:`Datafile <pyDataverse.models.Datafile` and attach it to a Dataset.

>>> from pyDataverse.models import Datafile
>>> df = Datafile()

Again, import your metadata (:meth:`from_json() <pyDataverse.models.Datafile.from_json>`).
Then set your PID and filename manually (:meth:`set() <pyDataverse.models.Datafile.set>`),
as they are required metadata for the upload.

>>> df_filename = "tests/data/datafile.txt"
>>> df.set({"pid": ds_pid, "filename": df_filename})
>>> df.get()
{'pid': '{DOI}', 'filename': 'tests/data/datafile.txt'}

Upload the Datafile with :meth:`upload_datafile() <pyDataverse.api.upload_datafile>`.

>>> resp = api.upload_datafile(ds_pid, df_filename, df.json())
>>> resp.json()
{'status': 'OK', 'data': {'files': [{'description': '', 'label': 'datafile.txt', 'restricted': False, 'version': 1, 'datasetVersionId': {DATASET_ID}, 'dataFile': {'id': {DATAFILE_ID}, 'persistentId': '', 'pidURL': '', 'filename': 'datafile.txt', 'contentType': 'text/plain', 'filesize': 7, 'description': '', 'storageIdentifier': '1765ceb4c37-c73707434835', 'rootDataFileId': -1, 'md5': '8b8db3dfa426f6bdb1798d578f5239ae', 'checksum': {'type': 'MD5', 'value': '8b8db3dfa426f6bdb1798d578f5239ae'}, 'creationDate': 'YYYY-MM-DD'}}]}}

By uploading the Datafile, you have made changes to the Dataset it is in. This leads to
a new Dataset version as Draft, unpublished. To make the changes available and
create a new Dataset version, publish the Dataset again
(:meth:`publish_dataset() <pyDataverse.api.publish_dataset>`).
Set the ``release_type="major"`` (defaults to ``minor``), to create version 2.0.

>>> resp = api.publish_dataset(ds_pid, release_type="major")
Dataset {DOI} published.


Retrieve all created data in tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now you can retrieve the created data as a tree structure with
:meth:`get_children() <pyDataverse.api.get_children>`. You have to pass
the parent identifier (e. g. Dataverse alias or Dataset PID) and the 
children types to be collected (``datasets``, ``datafiles``).

>>> tree = api.get_children("pyDataverse_user-guide", children_types= ["datasets", "datafiles"])
>>> tree
[{'dataset_id': {DATASET_ID}, 'pid': '{DOI}', 'type': 'dataset', 'children': [{'datafile_id': {DATAFILE_ID}, 'filename': 'datafile.txt', 'label': 'datafile.txt', 'pid': '', 'type': 'datafile'}]}]


Remove created data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After creating a Dataverse with a Dataset, and adding a Datafile to it, let's
now remove the created data objects.

Attention: Don't remove data on a Dataverse production instance, if not 100% sure!!!

First, always start with the Dataset (it automatically removes the Datafiles attached).
Cause the Dataset has been published, you have to destroy it with
:meth:`delete_dataset() <pyDataverse.api.delete_dataset>`.
To delete a not-published Dataset, use
:meth:`delete_dataset() <pyDataverse.api.delete_dataset>` instead.

>>> resp = api.destroy_dataset(ds_pid)
Dataset {'status': 'OK', 'data': {'message': 'Dataset :persistentId destroyed'}} destroyed

When you now want to retrieve the Dataset with
:meth:`get_dataset() <pyDataverse.api.get_dataset>`, pyDataverse throws an
:class:`OperationFailedError <pyDataverse.exceptions.OperationFailedError>`
exception, which is expected, as the Dataset was deleted before.

>>> resp = api.get_dataset(ds_pid)
pyDataverse.exceptions.OperationFailedError: ERROR: GET HTTP 404 - {BASE_URL}/api/v1/datasets/:persistentId/?persistentId={DOI}. MSG: {"status":"ERROR","message":"Dataset with Persistent ID {DOI} not found."}

Once the Dataset is removed, we only have to delete the Dataverse
(:meth:`delete_dataverse() <pyDataverse.api.delete_dataverse>`) to establish
the original state of the Dataverse instance.

>>> resp = api.delete_dataverse("pyDataverse_user-guide")
Dataverse pyDataverse_user-guide deleted.
