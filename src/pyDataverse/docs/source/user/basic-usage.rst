.. _user_basic-usage:

Basic Usage
=================

To get started, we will import metadata from JSON-files, create data objects
- one Dataverse, Dataset and Datafile - from it and clean up at the end.

The data for this tutorial can be found inside ``tests/data/basic-usage/``.

In addition to this tutorial, you can find more advanced stuff at
:ref:`User Guide - Advanced Usage <user_advanced-usage>` and
:ref:`User Guide - Use-Cases <user_use-cases>`.

Attention: The API responses may vary by each request and Dataverse instance!

**Requirements**

- pyDataverse installed (see :ref:`Installation <user_installation>`)

**Information**

- Follow the order of code execution
- Dataverse Docker 4.18.1 used
- pyDataverse 0.2.1 used
- API responses may vary cause of differing Dataverse instance

.. include:: ../snippets/warning_production.rst

**Additional Resources**

- Additional data from ``tests/data/user-guide/`` used (`GitHub repo <https://github.com/gdcc/pyDataverse/tree/develop/tests/data/user-guide>`_)

.. _user_basic-usage_api-connection:

1. Connect to Native API
------------------------------------------

First, create a :class:`NativeApi <pyDataverse.api.NativeApi>` instance to use it
later for the data creations. Replace ``{BASE_URL}`` (without trailing slash) and
``{API_TOKEN}`` with your instance specific values. Pay attention, that the
API-Token related user has proper rights. For this tutorial a Dataverse Docker
instance was used, running locally.

::

    >>> from pyDataverse.api import NativeApi
    >>> base_url = "{BASE_URL}"  # e.g. https://demo.dataverse.org
    >>> api_token = "{API_TOKEN}"
    >>> api = NativeApi(base_url, api_token)

Check with :meth:`get_info_version() <pyDataverse.api.NativeApi.get_info_version>`,
if our API connection works and get the version of the Dataverse instance.

::

    >>> resp = api.get_info_version()

All API requests return a :class:`requests.Response <requests.Response>` object, which
can then be used (e. g. :meth:`json() <requests.Response.json>`).

::

    >>> resp.json()
    {'status': 'OK', 'data': {'version': '4.15.1', 'build': '1377-701b56b'}}
    >>> resp.status_code
    200


.. _user_basic-usage_create-dataverse:

2. Create Dataverse
-----------------------------

The top-level data type is a Dataverse, so we will start with that.

First, instantiate a :class:`Dataverse <pyDataverse.models.Dataverse>`
object and import the metadata from a JSON-file with
:meth:`from_json() <pyDataverse.models.Dataverse.from_json>`.

For this tutorial, the files mentioned in "Additional Resources" were used and
placed in the root directory.

::

    >>> from pyDataverse.models import Dataverse
    >>> from pyDataverse.utils import read_file
    >>> dv = Dataverse()
    >>> dv_filename = "dataverse.json"
    >>> dv.from_json(read_file(dv_filename))

:meth:`get() <pyDataverse.models.Dataverse.get>` outputs the metadata imported as
a :class:`dict`.

::

    >>> dv.get()
    {'alias': 'pyDataverse_user-guide', 'name': 'pyDataverse - User Guide', 'dataverseContacts': [{'contactEmail': 'info@aussda.at'}]}
    >>> type(dv.get())
    <class 'dict'>

You can output the metadata with :meth:`json() <pyDataverse.models.Dataverse.json>`
as JSON, which defaults to the needed format for the Dataverse API upload
(equivalent to ``json(data_format="dataverse_upload")``).

::

    >>> dv.json()
    '{\n  "alias": "pyDataverse_user-guide",\n  "dataverseContacts": [\n    {\n      "contactEmail": "info@aussda.at"\n    }\n  ],\n  "name": "pyDataverse - User Guide"\n}'
    >>> type(dv.json())
    <class 'str'>

Then use :meth:`create_dataverse() <pyDataverse.api.NativeApi.create_dataverse>`, to
upload the Dataverse metadata to your Dataverse instance and create an
unpublished Dataverse Draft. You have to pass the parent Dataverse alias and the
metadata as JSON (:meth:`json() <pyDataverse.models.Dataverse.json>`).

::

    >>> resp = api.create_dataverse(":root", dv.json())
    Dataverse pyDataverse_user-guide created.

Last, publish the Dataverse Draft with
:meth:`publish_dataverse() <pyDataverse.api.NativeApi.publish_dataverse>`.

::

    >>> resp = api.publish_dataverse("pyDataverse_user-guide")
    Dataverse pyDataverse_user-guide published.

We can now retrieve the Dataverse with
:meth:`get_dataverse() <pyDataverse.api.NativeApi.get_dataverse>`.

::

    >>> resp = api.get_dataverse("pyDataverse_user-guide")
    >>> resp.json()
    {'status': 'OK', 'data': {'id': 441, 'alias': 'pyDataverse_user-guide', 'name': 'pyDataverse - User Guide', 'dataverseContacts': [{'displayOrder': 0, 'contactEmail': 'info@aussda.at'}], 'permissionRoot': True, 'dataverseType': 'UNCATEGORIZED', 'ownerId': 1, 'creationDate': '2021-01-13T20:47:43Z'}}

This is it! We created our first Dataverse data object through the
Dataverse API with the help of pyDataverse.

.. _user_basic-usage_create-dataset:

3. Create Dataset
-----------------------------

Instantiate an empty :class:`Dataset <pyDataverse.models.Dataverse>` first.

::

    >>> from pyDataverse.models import Dataset
    >>> ds = Dataset()

Same as for the Dataverse, use :meth:`from_json() <pyDataverse.models.Dataset.from_json>` to import
the metadata from your JSON-file.

::

    >>> ds_filename = "dataset.json"
    >>> ds.from_json(read_file(ds_filename))

As you can see, the models are pretty similiar. You can also use
:meth:`get() <pyDataverse.models.Dataset.get>`
to output your metadata.

::

    >>> ds.get()
    {'citation_displayName': 'Citation Metadata', 'title': 'Youth in Austria 2005', 'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1'}], 'datasetContact': [{'datasetContactEmail': 'ContactEmail1@mailinator.com', 'datasetContactName': 'LastContact1, FirstContact1'}], 'dsDescription': [{'dsDescriptionValue': 'DescriptionText'}], 'subject': ['Medicine, Health and Life Sciences']}

To validate, if the objects data is valid to create the JSON for
the Dataverse API upload, use :meth:`validate_json() <pyDataverse.Dataset.validate_json>`.
It validates against the
`Dataset JSON schema <https://github.com/gdcc/pyDataverse/blob/master/src/pyDataverse/schemas/json/dataset_upload_default_schema.json>`_
from ``src/pyDataverse/schemas/json/dataset_upload_default_schema.json``.

::

    >>> ds.validate_json()
    True

Now, let's manipulate the object a bit and change the title before we upload it.
With :meth:`set() <pyDataverse.models.Dataset.set>` you can pass any attribute you want
as a collection of key-value pairs in a :class:`dict`. Use the attribute name as a key
and add as many as you want.

::

    >>> ds.get()["title"]
    Youth in Austria 2005
    >>> ds.set({"title": "Youth from Austria 2005"})
    >>> ds.get()["title"]
    Youth from Austria 2005

To upload the Dataset with :meth:`create_dataset() <pyDataverse.api.NativeApi.create_dataset>`,
you have to tell to which Dataverse the Dataset gets attached to and pass the
metadata as a JSON string (:meth:`json() <pyDataverse.models.Dataset.json>`).

::

    >>> resp = api.create_dataset("pyDataverse_user-guide", ds.json())
    Dataset with pid 'doi:10.5072/FK2/EO7BNB' created.
    >>> resp.json()
    {'status': 'OK', 'data': {'id': 442, 'persistentId': 'doi:10.5072/FK2/EO7BNB'}}

For further usage in the tutorial, we need to save the created PID (short for
Persistent Identifier, which in our case is the DOI).

::

    >>> ds_pid = resp.json()["data"]["persistentId"]

You can now create a private Dataset URL with 
:meth:`create_dataset_private_url() <pyDataverse.api.NativeApi.create_dataset_private_url>`.

::

    >>> resp = api.create_dataset_private_url(ds_pid)
    Dataset private URL created: http://demo.dataverse.org/privateurl.xhtml?token={PRIVATE_TOKEN}
    >>> resp.json()
    {'status': 'OK', 'data': {'token': '{PRIVATE_TOKEN}', 'link': 'http://demo.dataverse.org/privateurl.xhtml?token={PRIVATE_TOKEN}', 'roleAssignment': {'id': 174, 'assignee': '#442', 'roleId': 8, '_roleAlias': 'member', 'privateUrlToken': '{PRIVATE_TOKEN}', 'definitionPointId': 442}}}

Finally, to make the Dataset public, publish the Draft with
:meth:`publish_dataset() <pyDataverse.api.NativeApi.publish_dataset>`.
Set the ``release_type="major"`` (defaults to ``minor``), to create version 1.0.

::

    >>> resp = api.publish_dataset(ds_pid, release_type="major")
    Dataset doi:10.5072/FK2/EO7BNB published


.. _user_basic-usage_upload-datafile:

4. Upload Datafile
-----------------------------

Last, we upload a :class:`Datafile <pyDataverse.models.Datafile>` and attach it to a Dataset.

::

    >>> from pyDataverse.models import Datafile
    >>> df = Datafile()

Again, import your metadata with :meth:`from_json() <pyDataverse.models.Datafile.from_json>`.
Then set your PID and filename manually (:meth:`set() <pyDataverse.models.Datafile.set>`),
as they are required as metadata for the upload.

::

    >>> df_filename = "datafile.txt"
    >>> df.set({"pid": ds_pid, "filename": df_filename})
    >>> df.get()
    {'pid': 'doi:10.5072/FK2/EO7BNB', 'filename': 'datafile.txt'}

Upload the Datafile with :meth:`upload_datafile() <pyDataverse.api.NativeApi.upload_datafile>`.

::

    >>> resp = api.upload_datafile(ds_pid, df_filename, df.json())
    >>> resp.json()
    {'status': 'OK', 'data': {'files': [{'description': '', 'label': 'datafile.txt', 'restricted': False, 'version': 1, 'datasetVersionId': 101, 'dataFile': {'id': 443, 'persistentId': '', 'pidURL': '', 'filename': 'datafile.txt', 'contentType': 'text/plain', 'filesize': 7, 'description': '', 'storageIdentifier': '176fd85f46f-cf06cf243502', 'rootDataFileId': -1, 'md5': '8b8db3dfa426f6bdb1798d578f5239ae', 'checksum': {'type': 'MD5', 'value': '8b8db3dfa426f6bdb1798d578f5239ae'}, 'creationDate': '2021-01-13'}}]}}

By uploading the Datafile, changes to the Dataset it is attached to have been made.
This means, a new unpublished Dataset version was created as a Draft and the changes
are not publicly available. To make them available and create a new Dataset version,
publish the Dataset again with
:meth:`publish_dataset() <pyDataverse.api.NativeApi.publish_dataset>`.
Again, set the ``release_type="major"`` to create version 2.0.

::

    >>> resp = api.publish_dataset(ds_pid, release_type="major")
    Dataset doi:10.5072/FK2/EO7BNB published


.. _user_basic-usage_get-data-tree:

5. Retrieve all created data in a Dataverse tree
---------------------------------------------------------

PyDataverse offers a special functionality: to retrieve a data tree from
a parent-node down, with all its children in it (Dataverses, Datasets and Datafiles).
Simply pass the identifier of the parent (e. g. Dataverse alias or Dataset
PID) and a list of children types to be collected (``datasets``, ``datafiles``) to
:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`.

::

    >>> tree = api.get_children("pyDataverse_user-guide", children_types= ["datasets", "datafiles"])
    >>> tree
    [{'dataset_id': 442, 'pid': 'doi:10.5072/FK2/EO7BNB', 'type': 'dataset', 'children': [{'datafile_id': 443, 'filename': 'datafile.txt', 'label': 'datafile.txt', 'pid': '', 'type': 'datafile'}]}]


.. _user_basic-usage_remove-data:

6. Remove created data
-----------------------------

After creating a Dataverse with a Dataset, and adding a Datafile to it, let's
now clean up the created data objects.

**Attention: Don't remove data on a Dataverse production instance, if not 100% sure!**

Always start with the Dataset. It automatically removes the Datafile(s) attached.
Cause the Dataset has been published, you have to destroy it with
:meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>`.
To delete a not-published Dataset Draft, use
:meth:`delete_dataset() <pyDataverse.api.NativeApi.delete_dataset>` instead.

::

    >>> resp = api.destroy_dataset(ds_pid)
    Dataset {'status': 'OK', 'data': {'message': 'Dataset :persistentId destroyed'}} destroyed

When you now want to retrieve the Dataset with
:meth:`get_dataset() <pyDataverse.api.NativeApi.get_dataset>`, pyDataverse throws an
:class:`OperationFailedError <pyDataverse.exceptions.OperationFailedError>`
exception, which is the expected behaviour, as the Dataset was deleted.

::

    >>> resp = api.get_dataset(ds_pid)
    pyDataverse.exceptions.OperationFailedError: ERROR: GET HTTP 404 - http://localhost:8085/api/v1/datasets/:persistentId/?persistentId=doi:10.5072/FK2/EO7BNB. MSG: {"status":"ERROR","message":"Dataset with Persistent ID doi:10.5072/FK2/EO7BNB not found."}

Once the Dataset is removed, we only have to delete the Dataverse
(:meth:`delete_dataverse() <pyDataverse.api.NativeApi.delete_dataverse>`) to establish
the original state of the Dataverse instance.

::

    >>> resp = api.delete_dataverse("pyDataverse_user-guide")
    Dataverse pyDataverse_user-guide deleted.
