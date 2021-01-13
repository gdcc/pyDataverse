.. _user_advanced-usage:

Advanced Usage
=================

The advanced usage tutorials should give you a deeper understanding of the
usage of pyDataverse through more specific use-cases.

For your first steps, please have a look at
:ref:`User Guide - Basic Usage <user_advanced-usage>`.

More use-cases can be found at :ref:`User Guide - Use-Cases <user_use-cases>`.

**Information**

Attention: API responses may vary cause of differing Dataverse instance

.. include:: ../snippets/warning_production.rst

.. _advanced-usage_data-migration:

1. CSV 2 Dataverse data migration
-----------------------------------------------

Importing lots of data from data sources outside dataverse can be done
with the help of the :ref:`CSV templates <user_csv-templates>`.

Add your data to the CSV files, no matter where the data comes from (humans or machines).
The CSV format can be used as a bridge from another source origin (e.g. programming
language, data format) or filled directly by humans who collect the data manually.

Once you have the data, import it into pyDataverse and upload it via the Dataverse API.

**Requirements**

- pyDataverse installed (see :ref:`install <user_installation>`)

**Information**

- Follow the order of code execution
- Dataverse Docker 4.18.1 used
- pyDataverse 0.2.1 used

**Additional Resources**

- CSV templates from ``src/pyDataverse/templates/`` used (see :ref:`CSV templates <user_csv-templates>`)
- Additional data from ``tests/data/user-guide/`` used (`GitHub repo <https://github.com/gdcc/pyDataverse/tree/develop/tests/data/user-guide>`_)


.. _advanced-usage_data-migration_adapt-csv-templates:

1.1 Adapt CSV-templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Copy the CSV templates from ``src/pyDataverse/templates/`` and place them
in the root directory. Then adapt their structure to your needs (e. g. add
or remove columns). Find out more about how the CSV templates work at
:ref:`CSV templates <user_csv-templates>`.


.. _advanced-usage_data-migration_fill-csv-templates:

1.2 Add metadata to the CSV templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Collect data and add them in the pre-structured CSV files
(manually or programmatically), until all data needed is in.

Attention: Some columns must be entered in a JSON format!


.. _advanced-usage_data-migration_import-csv-templates:

1.3 Add datafiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add the files for the import mentioned in datafiles.csv to your root directory.


.. _advanced-usage_data-migration_import-csv-templates:

1.4 Import CSV templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Import the CSV templates into pyDataverse

First, import the CSV templates into as :class:`dict`s with
:meth:`read_csv_as_dicts() <pyDataverse.utils.read_csv_as_dicts>`.
This automatically removes the ``dv.`` prefix from the attributes,
converts boolean values and loads the JSON columns properly.

For this tutorial, the files mentioned in "Additional Resources" were used and
placed in the root directory.

::

    >>> import os
    >>> from pyDataverse.utils import read_csv_as_dicts
    >>> from pyDataverse.api import NativeApi
    >>> csv_datasets_filename = "datasets.csv"
    >>> ds_data = read_csv_as_dicts(csv_datasets_filename)
    >>> csv_datafiles_filename = "datafiles.csv"
    >>> df_data = read_csv_as_dicts(csv_datafiles_filename)

Second, loop over each entry, which is a Dataset. Each time, instantiate an empty
:class:`Dataset <pyDataverse.models.Dataset>`, add the data with
:meth:`set() <pyDataverse.models.Dataset.set>` and append the object to
a :class:`list`.

::

    >>> from pyDataverse.models import Dataset
    >>> ds_lst = []
    >>> for ds in ds_data:
    >>>     ds_obj = Dataset()
    >>>     ds_obj.set(ds)
    >>>     ds_lst.append(ds_obj)

Same for :class:`Datafile <pyDataverse.models.Datafile>`s with
:meth:`set() <pyDataverse.models.Datafile.set>`).

::

    >>> from pyDataverse.models import Datafile
    >>> df_lst = []
    >>> for df in df_data:
    >>>     df_obj = Datafile()
    >>>     df_obj.set(df)
    >>>     df_lst.append(df_obj)


.. _advanced-usage_data-migration_upload-data:

1.5 Upload data via API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before we can upload data, we must create an instance of
:class:`NativeApi <pyDataverse.api.NativeApi>`.
Replace ``{BASE_URL}`` (without trailing slash) and
``{API_TOKEN}`` with your instance specific values. Pay attention, that the
API-Token related user has proper rights. For this tutorial a Dataverse Docker
instance was used, running locally.

::

    >>> base_url = "{BASE_URL}"  # e.g. https://demo.dataverse.org
    >>> api_token = "{API_TOKEN}"
    >>> api = NativeApi(base_url, api_token)

Loop over the :class:`list <list>` of :class:`Dataset <pyDataverse.models.Dataset>`s,
upload the metadata with
:meth:`create_dataset() <pyDataverse.api.NativeApi.create_dataset>` and collect
all ``dataset_id``s and ``pid``s in ``dataset_id_2_pid`` for further use later on.

Attention: The Dataverse assigned to ``dv_alias`` must be published, to attach a Dataset to it.

::

    >>> dv_alias = ":root:"
    >>> dataset_id_2_pid = {}
    >>> for ds in ds_lst:
    >>>     resp = api.create_dataset(dv_alias, ds.json())
    >>>     dataset_id_2_pid[ds.get()["org.dataset_id"]] = resp.json()["data"]["persistentId"]
    Dataset with pid 'doi:10.5072/FK2/WVMDFE' created.

Same for the :class:`list <list>` of :class:`Datafile <pyDataverse.models.Datafile>`s with
:meth:`upload_datafile() <pyDataverse.api.NativeApi.upload_datafile>`.
Next to the metadata, the ``PID`` and the ``filename`` must be passed.

::

    >>> for df in df_lst:
    >>>     pid = dataset_id_2_pid[df.get()["org.dataset_id"]]
    >>>     filename = os.path.join(os.getcwd(), df.get()["org.filename"])
    >>>     df.set({"pid": pid, "filename": filename})
    >>>     resp = api.upload_datafile(pid, filename, df.json())


.. _advanced-usage_data-migration_publish-dataset:

1.6 Publish Datasets via API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, publish all Datasets with :meth:`publish_dataset() <pyDataverse.api.NativeApi.publish_dataset>`.

::

    >>> for dataset_id, pid in dataset_id_2_pid.items():
    >>>     resp = api.publish_dataset(pid, "major")
    >>>     resp.json()
    Dataset doi:10.5072/FK2/WVMDFE published
    {'status': 'OK', 'data': {'id': 444, 'identifier': 'FK2/WVMDFE', 'persistentUrl': 'https://doi.org/10.5072/FK2/WVMDFE', 'protocol': 'doi', 'authority': '10.5072', 'publisher': 'Root', 'publicationDate': '2021-01-13', 'storageIdentifier': 'file://10.5072/FK2/WVMDFE'}}
