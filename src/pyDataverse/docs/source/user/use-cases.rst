.. _user_use-cases:

Use-Cases
=================

For a basic introduction to pyDataverse, have a look at
:ref:`User Guide - Basic Usage <user_basic-usage>`.


.. _use-cases data-migration:

Data Migration
-----------------------------

Importing lots of data from data sources outside dataverse can be done
with the help of the CSV templates. Add your data to the CSV files, and
then import them into pyDataverse for the API upload at the end.


There is a tutorial, how you can do mass imports with the help of pyDataverses
CSV templates. Look at :ref:`User Guide - Advanced Usage <user_advanced-usage>`.


Testing
-----------------------------

**Create test data for integrity tests (DevOps)**

Get full lists of all Dataverses, Datasets and Datafiles of an instance,
or just a part of it. Store the results in seperated JSON files. They
can be used to do data integrity tests and look for data completeness
after an upgrade or Dataverse migration. They easily integrate into the
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_ for Jenkins.

* Collect a data tree with all Dataverses, Datasets and Datafiles (`get_children()`)
* Extract Dataverses, Datasets and Datafiles from the tree (`dataverse_tree_walker()`)
* Save extracted data (`save_dataverse_tree()`)

**Mass removal of data in Dataverse (DevOps)**

When you do testing, you often have to upload a collection of Dataverse,
with Datasets and Datafiles within in a tree structure. It can be
tricky to remove them automatically, but with the functions mentioned
above, you can collect the data first, needed for the removal later.

* Collect a data tree with all Dataverses and Datasets (`get_children()`)
* Extract Dataverses and Datasets from the tree (`dataverse_tree_walker()`)
* Save extracted data (`save_dataverse_tree()`)
* Iterate over Datasets and delete/destroy them (`delete_dataset()`, `destroy_dataset`)
* Iterate over Dataverses and delete them (`delete_dataverse()`)

This functionality is not so far in pyDataverse, but you can find it in
`aussda_tests <https://github.com/AUSSDA/aussda_tests/>`_.


.. _use-cases data-science:

Data Science pipeline integration
------------------------------------

Use data and/or metadata from a Dataverse instance, and get the data
by its API. Or you created data and want to automatically add
it to your Dataset. PyDataverse connects your Data Science pipeline
with your Dataverse instance.


.. _use-cases microservices:

Web-Applications / Microservices
-----------------------------

As it is a direct and easy way to access Dataverses API's and
to manipulate its data models, it integrates really well into
all kind of web-applications / microservices. For example, to
visualize data, do some analysis, enrich it with other data
sources and so on.
