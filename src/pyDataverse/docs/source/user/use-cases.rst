.. _user_use-cases:

Use-Cases
=================

For a basic introduction to pyDataverse, visit
:ref:`User Guide - Basic Usage <user_basic-usage>`. For information on more advanced uses, visit :ref:`User Guide - Advanced Usage <user_advanced-usage>`.


.. _use-cases_data-migration:

Data Migration
-----------------------------

Importing lots of data from data sources outside a Dataverse installation can be done
with the help of the :ref:`CSV templates <user_csv-templates>`.
Simply add your data to the CSV files, import the files into pyDataverse, and then
upload the data and metadata via the API.

The following mappings currently exist:

- CSV
  - CSV 2 pyDataverse (:ref:`Tutorial <advanced-usage_data-migration>`)
  - pyDataverse 2 CSV (:ref:`Tutorial <advanced-usage_data-migration>`)
- Dataverse Upload JSON
    - JSON 2 pyDataverse
    - pyDataverse to JSON

If you would like to add an additional mapping, we welcome
:ref:`contributions <contributing_contributing>`!


.. _use-cases_testing:

Testing
-----------------------------


.. _use-cases_testing_create-test-data:

Create test data for integrity tests (DevOps)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get full lists of all Dataverse collections, Datasets and Datafiles of an installation,
or a subset of it. The results are stored in JSON files, which then
can be used to do data integrity tests and verify data completeness.
This is typically useful after an upgrade or a Dataverse migration.
The data integrates easily into
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_ and to any CI
build tools.

The general steps for use:

- Collect a data tree with all Dataverse collections, Datasets and Datafiles (:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`)
- Extract Dataverse collections, Datasets and Datafiles from the tree (:func:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`)
- Save extracted data (:func:`save_tree_data() <pyDataverse.utils.save_tree_data>`)


.. _use-cases_testing_mass-removal:

Mass removal of data in a Dataverse installation (DevOps)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After testing, you often have to clean up Dataverse collections
with Datasets and Datafiles within. It can be
tricky to remove them all at once, but pyDataverse helps you to do it
with only a few commands:

- Collect a data tree with all Dataverse collections and Datasets (:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`)
- Extract Dataverse collections and Datasets from the tree (:func:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`)
- Save extracted data (:func:`save_tree_data() <pyDataverse.utils.save_tree_data>`)
- Iterate over all Datasets to delete/destroy them (:meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>` :meth:`delete_dataset() <pyDataverse.api.NativeApi.delete_dataset>`, :meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>`)
- Iterate over all Dataverse collections to delete them (:meth:`delete_dataverse() <pyDataverse.api.NativeApi.delete_dataverse>`)

This functionality is not yet fully implemented in pyDataverse,
but you can find it in
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_.


.. _use-cases_data-science:

Data Science Pipeline
------------------------------------

Using APIs, you can access data and/or metadata from a Dataverse installation. You can also use pyDataverse to automatically add data and metadata to your Dataset. PyDataverse connects your Data Science pipeline with your Dataverse installation.


.. _use-cases_microservices:

Web-Applications / Microservices
------------------------------------------

As it is a direct and easy way to access Dataverses API's and
to manipulate the Dataverse installation's data models, it integrates really well into
all kind of web-applications and microservices. For example, you can use pyDataverse to
visualize data, do some analysis, enrich it with other data
sources (and so on).
