.. _user_use-cases:

Use-Cases
=================

For a basic introduction to pyDataverse, have a look at
:ref:`User Guide - Basic Usage <user_basic-usage>`, for advanced
at :ref:`User Guide - Advanced Usage <user_advanced-usage>`.


.. _use-cases_data-migration:

Data Migration
-----------------------------

Importing lots of data from data sources outside dataverse can be done
with the help of the :ref:`CSV templates <user_csv-templates>`.
Add your data to the CSV files, import them into pyDataverse and
upload the data and metadata later on via the API.

- CSV 2 Dataverse (:ref:`Tutorial <advanced-usage_data-migration>`)
- Dataverse 2 Dataverse (mapping from Dataverse 2 pyDataverse missing)
- DSpace 2 Dataverse (mapping from DSpace 2 pyDataverse missing)
- NESSTAR 2 Dataverse (mapping from NESSTAR 2 pyDataverse missing)

It would be great to see some new mappings as
:ref:`contribution <contributing_contributing>`.


.. _use-cases_testing:

Testing
-----------------------------


.. _use-cases_testing_create-test-data:

Create test data for integrity tests (DevOps)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get full lists of all Dataverses, Datasets and Datafiles of an instance,
or a subset of it. The results are stored in JSON files, which then
can be used to do data integrity tests and look for data completeness.
This could typically applied after an upgrade or a Dataverse migration.
The data integrates easily into
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_ and to any CI
build tools.

- Collect a data tree with all Dataverses, Datasets and Datafiles (:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`)
- Extract Dataverses, Datasets and Datafiles from the tree (:func:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`)
- Save extracted data (:func:`save_tree_data() <pyDataverse.utils.save_tree_data>`)


.. _use-cases_testing_mass-removal:

Mass removal of data in Dataverse (DevOps)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After testing, you often have to clean up a collection of Dataverse,
with Datasets and Datafiles within. It can be
tricky to remove them all at once, but pyDataverse helps you to do it
only with a few commands:

- Collect a data tree with all Dataverses and Datasets (:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`)
- Extract Dataverses and Datasets from the tree (:func:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`)
- Save extracted data (:func:`save_tree_data() <pyDataverse.utils.save_tree_data>`)
- Iterate over all Datasets to delete/destroy them (:meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>` :meth:`delete_dataset() <pyDataverse.api.NativeApi.delete_dataset>`, :meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>`)
- Iterate over all Dataverses to delete them (:meth:`delete_dataverse() <pyDataverse.api.NativeApi.delete_dataverse>`)

This functionality is so far not fully implemented in pyDataverse,
but you can find it in
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_.


.. _use-cases_data-science:

Data Science Pipeline
------------------------------------

Use data and/or metadata from a Dataverse instance, and get the data
by its API. Or you created data and want to automatically add
it to your Dataset. PyDataverse connects your Data Science pipeline
with your Dataverse instance.


.. _use-cases_microservices:

Web-Applications / Microservices
------------------------------------------

As it is a direct and easy way to access Dataverses API's and
to manipulate its data models, it integrates really well into
all kind of web-applications / microservices. For example, to
visualize data, do some analysis, enrich it with other data
sources and so on.
