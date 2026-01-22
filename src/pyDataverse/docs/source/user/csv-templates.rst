.. _user_csv-templates:

CSV Templates
============================

.. _user_csv-templates_description:

General
-----------------------------

The CSV templates offer a **pre-defined data format**, which can be used to
import metadata into pyDataverse, and export from it.
They support all three Dataverse Software data-types: Dataverse collections, Datasets and Datafiles.

CSV is an open file format, and great for humans and for machines. It can be
opened with your Spreadsheet software and edited manually, or used by your
favoured programming language.

The CSV format can also work as an exchange format or kind of a bridge
between all kind of data formats and programming languages.

The CSV templates and the mentioned workflow below can be used especially for:

- **Mass imports into a Dataverse installation:** The data to be imported could ether be collected manually (e. g. digitization of paper works), or created by machines (coming from any data source you have).
- **Data exchange:** share pyDataverse data with any other system in an open, machine-readable format

The CSV templates are licensed under `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_


.. _user_csv-templates_data-format:

Data format
-----------------------------

- Separator: ``,``
- Encoding: ``utf-8``
- Quotation: ``"``. Note: In JSON strings, you have to escape with ``\`` before a quotation mark (e. g. adapt ``"`` to ``\"``).
- Boolean: we recommend using ``TRUE`` and ``FALSE`` as boolean values. Note: They can be modified, when you open it with your preferred spreadsheet software (e. g. Libre Office), depending on the software or your operating systems settings.


.. _user_csv-templates_content:

Content
-----------------------------

The templates don't come empty. They are pre-filled with supportive information to get started.
Each row is one entry

1. **Column names**: The attribute name for each column. You can add and remove columns as you want. The pre-filled columns are a recommendation, as they consist of all metadata for the specific data-type, and the most common internal fields for handling the workflow. This is the only row that's not allowed to be deleted. There are three established prefixes so far (you can define your own if you want):

  a. ``org.``: Organization specific information to handle the data workflow later on.
  b. ``dv.``: Dataverse specific metadata, used for API uploads. Use the exact Dataverse software attribute name after the prefix, so the metadata gets imported properly.
  c. ``alma.``: ALMA specific information

2. **Description:** Description of the Dataverse software attribute. This row is for support purposes only, and must be deleted before usage.
3. **Attribute type:** Describes the type of the attribute (``serial``, ``string`` or ``numeric``). Strings can also be valid JSON strings to use more complex data structures. This row is for support purposes only, and must be deleted before usage.
4. **Example:** Contains a concrete example. To start adding your own data, it is often good to get started by copying the example for it. This row is for support purposes only, and must be deleted before usage.
5. **Multiple:** ``TRUE``, if multiple entries are allowed (boolean). This row is for support purposes only, and must be deleted before usage.
6. **Sub-keys:** ``TRUE``, if sub-keys are part (boolean). Only applicable to JSON strings. This row is for support purposes only, and must be deleted before usage.


.. _user_csv-templates_usage:

Usage
-----------------------------

To use the CSV templates, we propose following steps as a best practice.
The workflow is the same for Dataverse collections, Datasets and Datafiles.

There is also a more detailed tutorial on how to use the CSV templates
for mass imports in the
:ref:`User Guide - Advanced <advanced-usage_data-migration>`.

The CSV templates can be found in ``pyDataverse/templates/``
(`GitHub repo <https://github.com/gdcc/pyDataverse/tree/master/pyDataverse/templates>`_):

- `dataverses.csv <https://raw.githubusercontent.com/gdcc/pyDataverse/master/pyDataverse/templates/dataverses.csv>`_
- `datasets.csv <https://raw.githubusercontent.com/gdcc/pyDataverse/master/pyDataverse/templates/datasets.csv>`_
- `datafiles.csv <https://raw.githubusercontent.com/gdcc/pyDataverse/master/pyDataverse/templates/datafiles.csv>`_


.. _user_csv-templates_usage_create-csv:

Adapt CSV template(s)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, adapt the CSV templates to your own needs and workflow.

#. **Open a template file and save it:** Just start by copying the file and changing its filename to something descriptive (e.g. ``20200117_datasets.csv``).
#. **Adapt columns:** Then change the pre-defined columns (attributes) to your needs.
#. **Add metadata:** Add metadata in the first empty row. Closely following the example is often a good starting point, especially for JSON strings.
#. **Remove supporting rows:** Once you are used to the workflow, you can delete the supportive rows 2 to 6. This must be done before you use the template for pyDataverse!
#. **Save and use:** Once you have finished editing, save the CSV-file and import it to pyDataverse.


.. _user_csv-templates_usage_add-metadata:

Use the CSV files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For further usage of the CSV files with pyDataverse, for example:

- adding metadata to the CSV files
- importing CSV files
- uploading data and metadata via API

... have a look at the :ref:`Data Migration Tutorial <advanced-usage_data-migration>`.


.. _user_csv-templates_usage_export-csv:

Export from pyDataverse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to export your metadata from a pyDataverse object (
:class:`Dataverse <pyDataverse.models.Dataverse>`,
:class:`Dataset <pyDataverse.models.Dataset>`,
:class:`Datafile <pyDataverse.models.Datafile>`)
to a CSV file:

#. Get the metadata as :class:`dict <dict>` (:meth:`Dataverse.get() <pyDataverse.models.Dataverse.get>`, :meth:`Dataset.get() <pyDataverse.models.Dataset.get>` or :meth:`Datafile.get() <pyDataverse.models.Datafile.get>`).
#. Pass the :class:`dict <dict>` to :func:`write_dicts_as_csv() <pyDataverse.utils.write_dicts_as_csv>`. Note: Use the internal attribute lists from ``pyDataverse.models`` to get a complete list of fieldnames for each Dataverse data-type (e. g. ``Dataset.__attr_import_dv_up_citation_fields_values``).


.. _user_csv-templates_resources:

Resources
-----------------------------

- Dataverse example data taken from `dataverse_full.json <https://github.com/AUSSDA/pyDataverse/blob/master/tests/data/dataverse_full.json>`_
- Dataset example data taken from `dataset_full.json <https://github.com/AUSSDA/pyDataverse/blob/master/tests/data/dataset_full.json>`_
- Datafile example data taken from `Native API documentation <http://guides.dataverse.org/en/latest/api/native-api.html#add-a-file-to-a-dataset>`_
