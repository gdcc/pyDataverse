.. _user_use-cases:

Use-Cases
=================

For a basic introduction to pyDataverse, have a look at
:ref:`User Guide - Basic Usage <user_basic-usage>`, for advanced
stuff at :ref:`User Guide - Advanced Usage <user_advanced-usage>`.


.. _use-cases_data-migration:

Data Migration
-----------------------------

Importing lots of data from data sources outside dataverse can be done
with the help of the CSV templates. Add your data to the CSV files, and
then import them into pyDataverse for the API upload at the end.

- CSV 2 Dataverse (:ref:`Tutorial <advanced-usage_data-migration>`)
- Dataverse 2 Dataverse (one mapping missing)
- DSpace 2 Dataverse (one mapping missing)
- NESSTAR 2 Dataverse (one mapping missing)


.. _use-cases_testing:

Testing
-----------------------------

**Create test data for integrity tests (DevOps)**

Get full lists of all Dataverses, Datasets and Datafiles of an instance,
or just a part of it. Store the results in seperated JSON files. They
can be used to do data integrity tests and look for data completeness
after an upgrade or Dataverse migration. They easily integrate into the
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_ for Jenkins.

- Collect a data tree with all Dataverses, Datasets and Datafiles (:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`)
- Extract Dataverses, Datasets and Datafiles from the tree (:func:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`)
- Save extracted data (:func:`save_dataverse_tree() <pyDataverse.utils.save_dataverse_tree>`)

**Mass removal of data in Dataverse (DevOps)**

When you do testing, you often have to upload a collection of Dataverse,
with Datasets and Datafiles within in a tree structure. It can be
tricky to remove them automatically, but with the functions mentioned
above, you can collect the data first, needed for the removal later.

- Collect a data tree with all Dataverses and Datasets (:meth:`get_children() <pyDataverse.api.NativeApi.get_children>`)
- Extract Dataverses and Datasets from the tree (:func:`dataverse_tree_walker() <pyDataverse.utils.dataverse_tree_walker>`)
- Save extracted data (:func:`save_dataverse_tree() <pyDataverse.utils.save_dataverse_tree>`)
- Iterate over Datasets and delete/destroy them (`destroy_dataset`:meth:`delete_dataset() <pyDataverse.api.NativeApi.delete_dataset>`, :meth:`destroy_dataset() <pyDataverse.api.NativeApi.destroy_dataset>`)
- Iterate over Dataverses and delete them (:meth:`delete_dataverse() <pyDataverse.api.NativeApi.delete_dataverse>`)

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
