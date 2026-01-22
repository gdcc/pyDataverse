.. _user_advanced-usage:

Advanced Usage
==============

In addition to these tutorials, you can find more basic examples at
:ref:`User Guide - Basic Usage <user_advanced-usage>`.
and use-cases
:ref:`User Guide - Use-Cases <user_use-cases>`.


.. _advanced-usage_data-migration:

Import CSV to Dataverse
-----------------------

This tutorial will show you how to mass-import metadata from pyDataverse's own
CSV format (see :ref:`CSV templates <user_csv-templates>`), create
pyDataverse objects from it (Datasets and Datafiles)
and upload the data and metadata through the API.

The CSV format in this case can work as an exchange format or kind of a bridge between all kind of data formats and programming languages. Note that this can be filled directly by humans who collect the data manually (such as in digitization projects) as well as through more common automation workflows.


.. _advanced-usage_prepare:

Prepare
^^^^^^^

**Requirements**

- pyDataverse installed (see :ref:`user_installation`)

**Information**

- Follow the order of code execution
- Dataverse Docker 4.18.1 used
- pyDataverse 0.3.0 used
- API responses may vary by each request and Dataverse installation!

.. include:: ../snippets/warning_production.rst

**Additional Resources**

- CSV templates from ``pyDataverse/templates/`` are used (see :ref:`CSV templates <user_csv-templates>`)
- Data from ``tests/data/user-guide/`` is used (`GitHub repo <https://github.com/gdcc/pyDataverse/tree/master/tests/data/user-guide>`_)


.. _advanced-usage_data-migration_adapt-csv-templates:

Adapt CSV template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See :ref:`CSV templates - Adapt CSV template(s) <user_csv-templates_usage_create-csv>`.


.. _advanced-usage_data-migration_fill-csv-templates:

Add metadata to the CSV files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After preparing the CSV files, the metadata will need to be collected (manually or programmatically). No matter the origin or the format, each row must contain one entity (Dataverse collection, Dataset or Datafile).

As mentioned in "Additional Resources" in the tutorial we use prepared data and place it in the root directory. You can ether use our files or fill in your own metadata with your own datafiles.

No matter what you choose, you have to have properly formatted CSV files
(``datasets.csv`` and ``datafiles.csv``) before moving on.

Don't forget: Some columns must be entered in a JSON format!


.. _advanced-usage_data-migration_add-datafiles:

Add datafiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the files you have filled in the ``org.filename`` cell in ``datafiles.csv``
and then place them in the root directory (or any other specified directory).


.. _advanced-usage_data-migration_import-csv-templates:

Import CSV files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import the CSV files with
:meth:`read_csv_as_dicts() <pyDataverse.utils.read_csv_as_dicts>`.
This creates a list of :class:`dict`'s, automatically imports
the Dataverse Software's own metadata attribute (``dv.`` prefix),
converts boolean values, and loads JSON cells properly.

::

    >>> import os
    >>> from pyDataverse.utils import read_csv_as_dicts
    >>> csv_datasets_filename = "datasets.csv"
    >>> ds_data = read_csv_as_dicts(csv_datasets_filename)
    >>> csv_datafiles_filename = "datafiles.csv"
    >>> df_data = read_csv_as_dicts(csv_datafiles_filename)

Once we have the data in Python, we can easily import the data into
pyDataverse.

For this, loop over each Dataset :class:`dict`, to:

#. Instantiate an empty :class:`Dataset <pyDataverse.models.Dataset>`
#. add the data with :meth:`set() <pyDataverse.models.Dataset.set>` and
#. append the instance to a :class:`list`.

::

    >>> from pyDataverse.models import Dataset
    >>> ds_lst = []
    >>> for ds in ds_data:
    >>>     ds_obj = Dataset()
    >>>     ds_obj.set(ds)
    >>>     ds_lst.append(ds_obj)

To import the :class:`Datafile <pyDataverse.models.Datafile>`'s, do
the same with ``df_data``:
:meth:`set() <pyDataverse.models.Datafile.set>` the Datafile metadata, and
append it.

::

    >>> from pyDataverse.models import Datafile
    >>> df_lst = []
    >>> for df in df_data:
    >>>     df_obj = Datafile()
    >>>     df_obj.set(df)
    >>>     df_lst.append(df_obj)


.. _advanced-usage_data-migration_upload-data:

Upload data via API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before we can upload metadata and data, we need to create an instance of
:class:`NativeApi <pyDataverse.api.NativeApi>`.
You will need to replace the following variables with your own Dataverse installation's data
before executing the lines:

- BASE_URL: Base URL of your Dataverse installation, without trailing slash (e. g. ``https://data.aussda.at``))
- API_TOKEN: API token of a Dataverse user with proper rights to create a Dataset and upload Datafiles

::

    >>> from pyDataverse.api import NativeApi
    >>> api = NativeApi(BASE_URL, API_TOKEN)

Loop over the :class:`list <list>` of :class:`Dataset <pyDataverse.models.Dataset>`'s,
upload the metadata with
:meth:`create_dataset() <pyDataverse.api.NativeApi.create_dataset>` and collect
all ``dataset_id``'s and ``pid``'s in ``dataset_id_2_pid``.

Note: The Dataverse collection assigned to ``dv_alias`` must be published in order to add a Dataset to it.

::

    >>> dv_alias = ":root:"
    >>> dataset_id_2_pid = {}
    >>> for ds in ds_lst:
    >>>     resp = api.create_dataset(dv_alias, ds.json())
    >>>     dataset_id_2_pid[ds.get()["org.dataset_id"]] = resp.json()["data"]["persistentId"]
    Dataset with pid 'doi:10.5072/FK2/WVMDFE' created.

The API requests always return a
:class:`httpx.Response <httpx.Response>` object, which can then be used
to extract the data.

Next, we'll do the same for the :class:`list <list>` of
:class:`Datafile <pyDataverse.models.Datafile>`'s with
:meth:`upload_datafile() <pyDataverse.api.NativeApi.upload_datafile>`.
In addition to the metadata, the ``PID`` (Persistent Identifier, which is mostly the DOI) and the ``filename`` must be passed.

::

    >>> for df in df_lst:
    >>>     pid = dataset_id_2_pid[df.get()["org.dataset_id"]]
    >>>     filename = os.path.join(os.getcwd(), df.get()["org.filename"])
    >>>     df.set({"pid": pid, "filename": filename})
    >>>     resp = api.upload_datafile(pid, filename, df.json())

Now we have created all Datasets, which we added to ``datasets.csv``, and uploaded
all Datafiles, which we placed in the root directory, to the Dataverse installation.


.. _advanced-usage_data-migration_publish-dataset:

Publish Datasets via API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, we iterate over all Datasets and publish them with
:meth:`publish_dataset() <pyDataverse.api.NativeApi.publish_dataset>`.

::

    >>> for dataset_id, pid in dataset_id_2_pid.items():
    >>>     resp = api.publish_dataset(pid, "major")
    >>>     resp.json()
    Dataset doi:10.5072/FK2/WVMDFE published
    {'status': 'OK', 'data': {'id': 444, 'identifier': 'FK2/WVMDFE', 'persistentUrl': 'https://doi.org/10.5072/FK2/WVMDFE', 'protocol': 'doi', 'authority': '10.5072', 'publisher': 'Root', 'publicationDate': '2021-01-13', 'storageIdentifier': 'file://10.5072/FK2/WVMDFE'}}


The Advanced Usage tutorial is now finished! If you want to
revisit basic examples and use cases you can do so at
:ref:`User Guide - Basic Usage <user_basic-usage>` and
:ref:`User Guide - Use-Cases <user_use-cases>`.
