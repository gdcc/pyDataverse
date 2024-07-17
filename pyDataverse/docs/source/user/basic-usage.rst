.. _user_basic-usage:

Basic Usage
=================

This tutorial will show you how to import metadata from the Dataverse software's own
JSON format, create pyDataverse objects from it (Dataverse collection, Dataset
and Datafile), upload it via the API, and clean up at the end.

In addition to this tutorial, you can find more advanced examples at
:ref:`User Guide - Advanced Usage <user_advanced-usage>` and background information at
:ref:`User Guide - Use-Cases <user_use-cases>`.


.. _user_basic-usage_prepare:

Prepare
------------------------------------------

**Requirements**

- pyDataverse installed (see :ref:`Installation <user_installation>`)

**Basic Information**

- Follow the order of code execution
- Dataverse Docker 4.18.1 used
- pyDataverse 0.3.0 used
- API responses may vary by each request and Dataverse installation!

.. include:: ../snippets/warning_production.rst

**Additional Resources**

- Data from ``tests/data/user-guide/`` used (`GitHub repo <https://github.com/gdcc/pyDataverse/tree/master/tests/data/user-guide>`_)


.. _user_basic-usage_api-connection:

Connect to Native API
------------------------------------------

First, create a :class:`NativeApi <pyDataverse.api.NativeApi>` instance. You will use it
later for data creation. Replace the following variables with your own installation's data
before you execute the lines:

- BASE_URL: Base URL of your Dataverse installation, without trailing slash (e. g. ``https://data.aussda.at``))
- API_TOKEN: API token of a Dataverse installation user with proper permissions to create a Dataverse collection, create a Dataset, and upload Datafiles

::

    >>> from pyDataverse.api import NativeApi
    >>> api = NativeApi(BASE_URL, API_TOKEN)

Check with :meth:`get_info_version() <pyDataverse.api.NativeApi.get_info_version>`,
if the API connection works and to retrieve the version of your Dataverse instance:

::

    >>> resp = api.get_info_version()
    >>> resp.json()
    {'status': 'OK', 'data': {'version': '4.15.1', 'build': '1377-701b56b'}}
    >>> resp.status_code
    200

All API requests return a :class:`httpx.Response <httpx.Response>` object, which
can then be used (e. g. :meth:`json() <httpx.Response.json>`).


.. _user_basic-usage_create-dataverse:

Create Dataverse Collection
-----------------------------

The top-level data-type in the Dataverse software is called a Dataverse collection, so we will start with that. 
Take a look at the figure below to better understand the relationship between a Dataverse collection, a dataset, and a datafile. 

.. figure:: ../_images/collection_dataset.png
   :align: center
   :alt: collection dataset datafile

A dataverse collection (also known as a :class:`Dataverse <pyDataverse.models.Dataverse>`) acts as a container for your :class:`Datasets<pyDataverse.models.Dataverse>`.
It can also store other collections (:class:`Dataverses <pyDataverse.models.Dataverse>`).
You could create your own Dataverse collections, but it is not a requirement. 
A Dataset is a container for :class:`Datafiles<pyDataverse.models.Datafile>`, such as data, documentation, code, metadata, etc. 
You need to create a Dataset to deposit your files. All Datasets are uniquely identified with a DOI at Dataverse. 
For more detailed explanations, check out `the Dataverse User Guide <https://guides.dataverse.org/en/latest/user/dataset-management.html>`_.

Going back to the example, first, instantiate a :class:`Dataverse <pyDataverse.models.Dataverse>`
object and import the metadata from the Dataverse Software's own JSON format with
:meth:`from_json() <pyDataverse.models.Dataverse.from_json>`:

::

    >>> from pyDataverse.models import Dataverse
    >>> from pyDataverse.utils import read_file
    >>> dv = Dataverse()
    >>> dv_filename = "dataverse.json"
    >>> dv.from_json(read_file(dv_filename))

With :meth:`get() <pyDataverse.models.Dataverse.get>` you can
have a look at all the data of the object:

::

    >>> dv.get()
    {'alias': 'pyDataverse_user-guide', 'name': 'pyDataverse - User Guide', 'dataverseContacts': [{'contactEmail': 'info@aussda.at'}]}
    >>> type(dv.get())
    <class 'dict'>

To see only the metadata necessary for the Dataverse API upload, use
:meth:`json() <pyDataverse.models.Dataverse.json>`, which defaults
to the needed format for the Dataverse API upload
(equivalent to ``json(data_format="dataverse_upload")``):

::

    >>> dv.json()
    '{\n  "alias": "pyDataverse_user-guide",\n  "dataverseContacts": [\n    {\n      "contactEmail": "info@aussda.at"\n    }\n  ],\n  "name": "pyDataverse - User Guide"\n}'
    >>> type(dv.json())
    <class 'str'>

Then use :meth:`create_dataverse() <pyDataverse.api.NativeApi.create_dataverse>` to
upload the Dataverse metadata to your Dataverse installation via its Native API and
create an unpublished Dataverse collection draft. For this, you have to pass a) the parent
Dataverse collection alias to which the new Dataverse collection is attached and b) the metadata in the Dataverse Software's
own JSON format (:meth:`json() <pyDataverse.models.Dataverse.json>`):

::

    >>> resp = api.create_dataverse(":root", dv.json())
    Dataverse pyDataverse_user-guide created.

Last, we publish the Dataverse collection draft with
:meth:`publish_dataverse() <pyDataverse.api.NativeApi.publish_dataverse>`:

::

    >>> resp = api.publish_dataverse("pyDataverse_user-guide")
    Dataverse pyDataverse_user-guide published.

To have a look at the results of our work, you can check the created Dataverse collection
on the frontend, or use pyDataverse to retrieve the Dataverse collection with
:meth:`get_dataverse() <pyDataverse.api.NativeApi.get_dataverse>`:

::

    >>> resp = api.get_dataverse("pyDataverse_user-guide")
    >>> resp.json()
    {'status': 'OK', 'data': {'id': 441, 'alias': 'pyDataverse_user-guide', 'name': 'pyDataverse - User Guide', 'dataverseContacts': [{'displayOrder': 0, 'contactEmail': 'info@aussda.at'}], 'permissionRoot': True, 'dataverseType': 'UNCATEGORIZED', 'ownerId': 1, 'creationDate': '2021-01-13T20:47:43Z'}}

This is it, our first Dataverse collection created with the help of pyDataverse!
Now let's move on and apply what we've learned to Datasets and Datafiles.

.. _user_basic-usage_create-dataset:

Create Dataset
-----------------------------

Again, start by creating an empty pyDataverse object, this time a
:class:`Dataset <pyDataverse.models.Dataverse>`:

::

    >>> from pyDataverse.models import Dataset
    >>> ds = Dataset()

The function names often are the same for each data-type. So again, we can use
:meth:`from_json() <pyDataverse.models.Dataset.from_json>` to import
the metadata from the JSON file, but this time it feeds into a Dataset:

::

    >>> ds_filename = "dataset.json"
    >>> ds.from_json(read_file(ds_filename))

You can also use :meth:`get() <pyDataverse.models.Dataset.get>`
to output all data:

::

    >>> ds.get()
    {'citation_displayName': 'Citation Metadata', 'title': 'Youth in Austria 2005', 'author': [{'authorName': 'LastAuthor1, FirstAuthor1', 'authorAffiliation': 'AuthorAffiliation1'}], 'datasetContact': [{'datasetContactEmail': 'ContactEmail1@mailinator.com', 'datasetContactName': 'LastContact1, FirstContact1'}], 'dsDescription': [{'dsDescriptionValue': 'DescriptionText'}], 'subject': ['Medicine, Health and Life Sciences']}

Now, as the metadata is imported, we don't know if the data is valid and can be used
to create a Dataset. Maybe some attributes are missing or misnamed, or a
mistake during import happened. pyDataverse offers a convenient function
to test this out with
:meth:`validate_json() <pyDataverse.models.Dataset.validate_json>`, so
you can move on with confidence:


::

    >>> ds.validate_json()
    True

Adding or updating data manually is easy. With
:meth:`set() <pyDataverse.models.Dataset.set>`
you can pass any attribute you want as a collection of key-value
pairs in a :class:`dict`:

::

    >>> ds.get()["title"]
    Youth in Austria 2005
    >>> ds.set({"title": "Youth from Austria 2005"})
    >>> ds.get()["title"]
    Youth from Austria 2005

To upload the Dataset, use
:meth:`create_dataset() <pyDataverse.api.NativeApi.create_dataset>`.
You'll pass the Dataverse collection where the Dataset should be attached
and include the metadata as a JSON string
(:meth:`json() <pyDataverse.models.Dataset.json>`):

::

    >>> resp = api.create_dataset("pyDataverse_user-guide", ds.json())
    Dataset with pid 'doi:10.5072/FK2/EO7BNB' created.
    >>> resp.json()
    {'status': 'OK', 'data': {'id': 442, 'persistentId': 'doi:10.5072/FK2/EO7BNB'}}

Save the created PID (short for Persistent Identifier, which in
our case is the DOI) in a :class:`dict`:

::

    >>> ds_pid = resp.json()["data"]["persistentId"]

Private Dataset URL's can also be created. Use
:meth:`create_dataset_private_url() <pyDataverse.api.NativeApi.create_dataset_private_url>`
to get the URL and the private token:

::

    >>> resp = api.create_dataset_private_url(ds_pid)
    Dataset private URL created: http://data.aussda.at/privateurl.xhtml?token={PRIVATE_TOKEN}
    >>> resp.json()
    {'status': 'OK', 'data': {'token': '{PRIVATE_TOKEN}', 'link': 'http://data.aussda.at/privateurl.xhtml?token={PRIVATE_TOKEN}', 'roleAssignment': {'id': 174, 'assignee': '#442', 'roleId': 8, '_roleAlias': 'member', 'privateUrlToken': '{PRIVATE_TOKEN}', 'definitionPointId': 442}}}

Finally, to make the Dataset public, publish the draft with
:meth:`publish_dataset() <pyDataverse.api.NativeApi.publish_dataset>`.
Set ``release_type="major"`` (defaults to ``minor``), to create version 1.0:

::

    >>> resp = api.publish_dataset(ds_pid, release_type="major")
    Dataset doi:10.5072/FK2/EO7BNB published


.. _user_basic-usage_upload-datafile:

Upload Datafile
-----------------------------

After all the preparations, it's now time to upload a
:class:`Datafile <pyDataverse.models.Datafile>` and attach it to the Dataset:

::

    >>> from pyDataverse.models import Datafile
    >>> df = Datafile()

Again, import your metadata with :meth:`from_json() <pyDataverse.models.Datafile.from_json>`.
Then, set your PID and filename manually (:meth:`set() <pyDataverse.models.Datafile.set>`),
as they are required as metadata for the upload and are created during the
import process:

::

    >>> df_filename = "datafile.txt"
    >>> df.set({"pid": ds_pid, "filename": df_filename})
    >>> df.get()
    {'pid': 'doi:10.5072/FK2/EO7BNB', 'filename': 'datafile.txt'}

Upload the Datafile with
:meth:`upload_datafile() <pyDataverse.api.NativeApi.upload_datafile>`.
Pass the PID, the Datafile filename and the Datafile metadata:

::

    >>> resp = api.upload_datafile(ds_pid, df_filename, df.json())
    >>> resp.json()
    {'status': 'OK', 'data': {'files': [{'description': '', 'label': 'datafile.txt', 'restricted': False, 'version': 1, 'datasetVersionId': 101, 'dataFile': {'id': 443, 'persistentId': '', 'pidURL': '', 'filename': 'datafile.txt', 'contentType': 'text/plain', 'filesize': 7, 'description': '', 'storageIdentifier': '176fd85f46f-cf06cf243502', 'rootDataFileId': -1, 'md5': '8b8db3dfa426f6bdb1798d578f5239ae', 'checksum': {'type': 'MD5', 'value': '8b8db3dfa426f6bdb1798d578f5239ae'}, 'creationDate': '2021-01-13'}}]}}

By uploading the Datafile, the attached Dataset gets an update.
This means that a new unpublished Dataset version is created as a draft
and the change is not yet publicly available. To make it available
through creating a new Dataset version, publish the Dataset with
:meth:`publish_dataset() <pyDataverse.api.NativeApi.publish_dataset>`.
Again, set the ``release_type="major"`` to create version 2.0, as a file change
always leads to a major version change:

::

    >>> resp = api.publish_dataset(ds_pid, release_type="major")
    Dataset doi:10.5072/FK2/EO7BNB published


.. _user_basic-usage_download-data:

Download and save a dataset to disk
----------------------------------------

You may want to download and explore an existing dataset from Dataverse. The following code snippet will show how to retrieve and save a dataset to your machine.

Note that if the dataset is public, you don't need to have an API_TOKEN. Furthermore, you don't even need to have a Dataverse account to use this functionality. The code would therefore look as follows:

::

    >>> from pyDataverse.api import NativeApi, DataAccessApi
    >>> from pyDataverse.models import Dataverse

    >>> base_url = 'https://dataverse.harvard.edu/'

    >>> api = NativeApi(base_url)
    >>> data_api = DataAccessApi(base_url)

However, you need to know the DOI of the dataset that you want to download. In this example, we use ``doi:10.7910/DVN/KBHLOD``, which is hosted on Harvard's Dataverse instance that we specified as ``base_url``. The code looks as follows:

::

    >>> DOI = "doi:10.7910/DVN/KBHLOD"
    >>> dataset = api.get_dataset(DOI)

As previously mentioned, every dataset comprises of datafiles, therefore, we need to get the list of datafiles by ID and save them on disk. That is done in the following code snippet:

::

    >>> files_list = dataset.json()['data']['latestVersion']['files']

    >>> for file in files_list:
    >>>     filename = file["dataFile"]["filename"]
    >>>     file_id = file["dataFile"]["id"]
    >>>     print("File name {}, id {}".format(filename, file_id))

    >>>     response = data_api.get_datafile(file_id)
    >>>     with open(filename, "wb") as f:
    >>>         f.write(response.content)
    File name cat.jpg, id 2456195

Please note that in this example, the dataset will be saved in the execution directory. You could change that by adding a desired path in the ``open()`` function above.


.. _user_basic-usage_get-data-tree:

Retrieve all created data as a Dataverse tree
---------------------------------------------------------

PyDataverse offers a convenient way to retrieve all children-data from a specific
Dataverse collection or Dataset down to the Datafile level (Dataverse collections, Datasets
and Datafiles).

Simply pass the identifier of the parent (e. g. Dataverse collection alias or Dataset
PID) and the list of the children data-types that should be collected
(``dataverses``, ``datasets``, ``datafiles``) to
:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`:


::

    >>> tree = api.get_children("pyDataverse_user-guide", children_types= ["datasets", "datafiles"])
    >>> tree
    [{'dataset_id': 442, 'pid': 'doi:10.5072/FK2/EO7BNB', 'type': 'dataset', 'children': [{'datafile_id': 443, 'filename': 'datafile.txt', 'label': 'datafile.txt', 'pid': '', 'type': 'datafile'}]}]

In our case, we don't use ``dataverses`` as children data-type, as there
is none inside the created Dataverse collection.

For further use of the tree, have a look at
:meth:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`
and :meth:`save_tree_data() <pyDataverse.utils.save_tree_data>`.


.. _user_basic-usage_remove-data:

Clean up and remove all created data
----------------------------------------

As we have created a Dataverse collection, created a Dataset, and uploaded a Datafile, we now will
remove all of it in order to clean up what we did so far.

The Dataset has been published in the step above, so we have to destroy it with
:meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>`.
To remove a non-published Dataset,
:meth:`delete_dataset() <pyDataverse.api.NativeApi.delete_dataset>`
must be used instead.

Note: When you delete a Dataset, it automatically deletes all attached
Datafile(s):

::

    >>> resp = api.destroy_dataset(ds_pid)
    Dataset {'status': 'OK', 'data': {'message': 'Dataset :persistentId destroyed'}} destroyed

When you want to retrieve the Dataset now with
:meth:`get_dataset() <pyDataverse.api.NativeApi.get_dataset>`, pyDataverse throws an
:class:`OperationFailedError <pyDataverse.exceptions.OperationFailedError>`
exception, which is the expected behaviour, as the Dataset was deleted:

::

    >>> resp = api.get_dataset(ds_pid)
    pyDataverse.exceptions.OperationFailedError: ERROR: GET HTTP 404 - http://data.aussda.at/api/v1/datasets/:persistentId/?persistentId=doi:10.5072/FK2/EO7BNB. MSG: {"status":"ERROR","message":"Dataset with Persistent ID doi:10.5072/FK2/EO7BNB not found."}

After removing all Datasets and/or Dataverse collections in it, delete the parent Dataverse collection
(:meth:`delete_dataverse() <pyDataverse.api.NativeApi.delete_dataverse>`).

Note: It is not possible to delete a Dataverse collection with any data (Dataverse collection or
Dataset) attached to it.

::

    >>> resp = api.delete_dataverse("pyDataverse_user-guide")
    Dataverse pyDataverse_user-guide deleted.

Now the Dataverse instance is as it was once before we started.

The Basic Usage tutorial is now finished, but maybe you want to
have a look at more advanced examples at
:ref:`User Guide - Advanced Usage <user_advanced-usage>` and at
:ref:`User Guide - Use-Cases <user_use-cases>` for more information.
