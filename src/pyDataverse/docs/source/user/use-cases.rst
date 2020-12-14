.. _user_use-cases:

Use-Cases
=================

To get a basic understanding of how pyDataverse works, have a look first
at the :ref:`User Guide - Basic Usage <user_basic-usage>`.

.. _use-cases data-migrations:

Data Migrations
-----------------------------

Importing lots of data from data sources outside dataverse can be done
with the help of the CSV templates. Add your data to the CSV files, and
then import them into pyDataverse for the API upload at the end.

**1. Adapt CSV-templates**

Copy the CSV templates from ``src/pyDataverse/templates/`` and place them
in the root directory. Then adapt their structure to your needs (e. g. add
or remove columns). Find out more about how the CSV templates
:ref:`here <user_csv-templates>`.

**2. Fill up the CSV-files with metadata**

Collect data and add them in the pre-structured CSV files
(manually or programmatically), until all data needed is in there.

**3. Import CSV-files**

Import data from the CSV-files into pyDataverses own data models.


Import the data with
:meth:`read_csv_as_dicts() <pyDataverse.utils.read_csv_as_dicts>`.

prefix with defaults

>>> import os
>>> from pyDataverse.utils import read_csv_as_dicts
>>> from pyDataverse.api import NativeApi
>>> csv_datasets_filename = "tests/data/user-guide/datasets.csv"
>>> ds_data = read_csv_as_dicts(csv_datasets_filename)
>>> csv_datafiles_filename = "tests/data/user-guide/datafiles.csv"
>>> df_data = read_csv_as_dicts(csv_datafiles_filename)

Create empty :class:`Datasets <pyDataverse.models.Dataset`, add data with
:meth:`set() <pyDataverse.models.Dataset.set>` and append them to
the :class:`list`. Attention: All columns in the CSV templates, which are
Dataverse related, have the prefix ``dv.``, which must be removed during the import.

>>> from pyDataverse.models import Dataset
>>> ds_lst = []
>>> for ds in ds_data:
>>>     ds_obj = Dataset()
>>>     ds_obj.set(ds)
>>>     ds_lst.append(ds_obj)

Same for Datafiles (:class:`Datafiles <pyDataverse.models.Datafile`,
:meth:`set() <pyDataverse.models.Datafile.set>`).

>>> from pyDataverse.models import Datafile
>>> df_lst = []
>>> for df in df_data:
>>>     df_obj = Datafile()
>>>     df_obj.set(df)
>>>     df_lst.append(df_obj)


**4. Upload data via API**

init api

>>> dv_alias = "{DV_ALIAS}"
>>> pid_lst = []
>>> base_url = "{BASE_URL}"  # e.g. https://demo.dataverse.org
>>> api_token = "{API_TOKEN}"  # @USERNAME e. g. dataverseAdmin
>>> api = NativeApi(base_url, api_token)

tell which dataverse
save mapping

>>> dataset_id_2_pid = {}
>>> for ds in ds_lst:
>>>     resp = api.create_dataset(dv_alias, ds.json())
>>>     dataset_id_2_pid[ds.get()["org.dataset_id"]] = resp.json()["data"]["persistentId"]

Upload Datafiles

>>> for df in df_lst:
>>>     pid = dataset_id_2_pid[df.get()["org.dataset_id"]]
>>>     filename = os.path.join(os.getcwd(), "tests/data/user-guide", df.get()["org.filename"])
>>>     df.set({"pid": pid, "filename": filename})
>>>     resp = api.upload_datafile(pid, filename, df.json())


**5. Publish Datasets via API**

Publish your data with :meth:`publish_dataset() <pyDataverse.api.publish_dataset>`.

>>> for pid in pid_lst:
>>>     resp = api.publish_dataset(pid)


Additional information:

- :ref:`CSV templates <user_csv-templates>`


.. _use-cases testing:

Testing
-----------------------------

**Use test data**


**Create test data for integrity tests (DevOps)**

Get full lists of all Dataverses, Datasets and Datafiles of an instance, or just a part of it. Store the results in seperated JSON files. They can be used to do data integrity tests and look for data completeness after an upgrade or Dataverse migration. They easily integrate into the [aussda_tests](https://github.com/AUSSDA/aussda_tests) for Jenkins.

* Collect a data tree with all Dataverses, Datasets and Datafiles (`get_children()`)
* Extract Dataverses, Datasets and Datafiles from the tree (`dataverse_tree_walker()`)
* Save extracted data (`save_dataverse_tree()`)


.. _use-cases data-science:

Data Science pipeline integration
------------------------------------


.. _use-cases microservices:

Microservices
-----------------------------
