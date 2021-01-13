.. _user_csv-templates:

CSV templates
============================

.. _user_csv-templates_description:

General
-----------------------------

The CSV templates offer a **pre-structured data format**, which can be used to
import to and export from pyDataverse.
They support all three Dataverse data-types: Dataverses, Datasets and Datafiles.

CSV is great for humans as for machines. It can be opened with your Spreadsheet
application and edited manually, or used by your favoured programming language.

The CSV templates and the mentioned workflow below, can be used especially for:

- **Mass imports of data into your Dataverse instance:** The data to be imported could ether be collected manually (e. g. digitization of paper works), or created by machines.
- **Data exchange:** share pyDataverse data with any other system in an open, machine-readable format

The CSV template files are licensed under `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_


.. _user_csv-templates_data-format:

Data format
-----------------------------

**CSV specific:**

- Seperator: ``,``
- Encoding: ``utf-8``
- Quotation: ``"``. Attention: In JSON strings, you have to escape with ``\`` before a quotation mark (``"`` to ``\"``).
- Boolean: we recommend using ``TRUE`` and ``FALSE`` as boolean values. Attention: they can be modified, when you open it with your prefered spreadsheet software (e. g. Libre Office), depending on their settings. Maybe you want to align it to template format.

**Rows:**

The templates don't come empty. They consist of helpful information to add your
own data and get started.

1. Column names: The attribute name for each column. Mostly, it's Dataverse metadata or organization specific information for handling the process. But you can add or remove columns as you want. This is the only row, which will still be in the CSV file later on for the import to pyDataverse.

  a. `org.`: organization specific information
  b. `dv.`: Dataverse metadata, with specific metadatablock attribute-name added after point denominator. Mark with this the metadata attributes, which are used by your Dataverse instance.
  c. `alma.`: ALMA specific metadata

2. Description: Description of the attribute. This row is for support, and must be deleted before useage.
3. Attribute type: Describes the type of the attribute (``serial``, ``string`` or ``numeric``). Strings can also be valid JSON strings to use more complex data structures. This row is for support, and must be deleted before useage.
4. Example: Offers an example for each attribute. They can be used as a starting point to create your own data. This row is for support, and must be deleted before useage.
5. Multiple: If multiple entries are allowed (boolean). This row is for support, and must be deleted before useage.
6. Sub-keys: If sub-keys are part. Only applicable to JSON strings.  This row is for support, and must be deleted before useage.


.. _user_csv-templates_usage:

Usage
-----------------------------

The CSV templates can be found inside ``src/pyDataverse/templates/``
(`GitHub repo <https://github.com/gdcc/pyDataverse/tree/master/src/pyDataverse/templates>`_):

- `dataverses.csv <https://raw.githubusercontent.com/gdcc/pyDataverse/master/src/pyDataverse/templates/dataverses.csv>`_
- `datasets.csv <https://raw.githubusercontent.com/gdcc/pyDataverse/master/src/pyDataverse/templates/datasets.csv>`_
- `datafiles.csv <https://raw.githubusercontent.com/gdcc/pyDataverse/master/src/pyDataverse/templates/datafiles.csv>`_

To use the CSV templates, we propose following steps as best-practice.
The workflow is the same for Dataverses, Datasets and Datafiles.

There is also a more detailed tutorial, on how to use the CSV templates
for mass imports at
:ref:`User Guide - Advanced <advanced-usage_data-migration>`.


.. _user_csv-templates_usage_create-csv:

Create CSV files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Open a template file and save it: The easiest and most intuitive way to work with the templates, is, to first open the template and save it somewhere new under a descriptive filename (e.g. ``20200117_datasets.csv``).
#. Adapt columns: The pre-defined columns (attributes) are only a suggestion by us. You can remove columns, which you don't need, or add new ones as you want.
#. Add rows: Start to enter new data entries in the first empty row. Each row is one entry (e. g. one Dataset). If you use JSON, pay attention to escape the quotation character in the JSON string (read above). You can keep the 2nd and 3rd row for this as long as you need the information inside to create proper data entries and as long as you don't use the file with pyDataverse.
#. Remove supporting rows: Once you are used to the workflow with the data-structure, you can delete the supportive rows 2 to 6. This must be done before you use the template for pyDataverse.
#. Save and use: Once you are finished with editing, save your CSV-file and use it.


.. _user_csv-templates_usage_import-csv:

Import into pyDataverse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the CSV templates with pyDataverse

Import your CSV-files into pyDataverse:

#. Import the data with :func:`read_csv_as_dicts() <pyDataverse.utils.read_csv_as_dicts>` to get a dictionary. 
#. Pass the dictionary to the ``set()`` function related to your data-type (:meth:`Dataverse.set() <pyDataverse.models.Dataverse.set>`, :meth:`Dataset.set() <pyDataverse.models.Dataset.set>` or :meth:`Datafile.set() <pyDataverse.models.Datafile.set>`)
#. Use the pyDataverse object, e. g. to upload it through the API.

.. _user_csv-templates_usage_export-csv:

Export from pyDataverse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Export pyDataverse objects (
:class:`Dataverse <pyDataverse.models.Dataverse>`,
:class:`Dataset <pyDataverse.models.Dataset>`,
:class:`Datafile <pyDataverse.models.Datafile>`) as CSV files:

#. Get your data from the pyDataverse object as :class:`dict <dict>` (:meth:`Dataverse.get() <pyDataverse.models.Dataverse.get>`, :meth:`Dataset.get() <pyDataverse.models.Dataset.get>` or :meth:`Datafile.get() <pyDataverse.models.Datafile.get>`).
#. Pass the :class:`dict <dict>` to :func:`write_dicts_as_csv() <pyDataverse.utils.write_dicts_as_csv>`. Hint: Use the internal attribute lists from pyDataverse.models to get a complete fieldnames list for each data model (e. g. ``Dataset.__attr_import_dv_up_citation_fields_values``).


.. _user_csv-templates_resources:

Resources
-----------------------------

- Dataverse Example: Data taken from `dataverse_full.json <https://github.com/AUSSDA/pyDataverse/blob/master/tests/data/dataverse_full.json>`_
- Dataset Example: Data taken from `dataset_full.json <https://github.com/AUSSDA/pyDataverse/blob/master/tests/data/dataset_full.json>`_
- Datafile Example: Data taken from `Native API documentation <http://guides.dataverse.org/en/latest/api/native-api.html#add-a-file-to-a-dataset>`_
