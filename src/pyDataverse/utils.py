# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions."""
from __future__ import absolute_import

import csv
import json
import pickle

from jsonschema import validate


def read_file(filename, mode="r", encoding="utf-8"):
    """Read in a file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    mode : str
        Read mode of file. Defaults to `r`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    Returns
    -------
    str
        Returns data as string.

    """
    assert isinstance(filename, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        data = f.read()

    assert isinstance(data, str)
    return data


def write_file(filename, data, mode="w", encoding="utf-8"):
    """Write data in a file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    data : str
        Data to be stored.
    mode : str
        Read mode of file. Defaults to `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    """
    assert isinstance(filename, str)
    assert isinstance(data, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        f.write(data)


def read_json(filename, mode="r", encoding="utf-8"):
    """Read in a json file.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    filename : str
        Filename with full path.
    mode : str
        Read mode of file. Defaults to `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    dict
        Data as a json-formatted string.

    """
    assert isinstance(filename, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        data = json.load(f)

    assert isinstance(data, dict)
    return data


def write_json(filename, data, mode="w", encoding="utf-8"):
    """Write data to a json file.

    Parameters
    ----------
    filename : str
        Filename with full path.
    data : dict
        Data to be written in the JSON file.
    mode : str
        Write mode of file. Defaults to `w`. See more at
        https://docs.python.org/3/library/functions.html#open
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    """
    assert isinstance(filename, str)
    assert isinstance(data, str)
    assert isinstance(mode, str)
    assert isinstance(encoding, str)

    with open(filename, mode, encoding=encoding) as f:
        json.dump(data, f, indent=2)


def read_pickle(filename):
    """Read in pickle file.

    See more at `pickle <https://docs.python.org/3/library/pickle.html>`_.

    Parameters
    ----------
    filename : str
        Full filename with path of file.

    Returns
    -------
    dict
        Data object.

    """
    assert isinstance(filename, str)

    with open(filename, "rb") as f:
        data = pickle.load(f)

        assert isinstance(data, dict)
        return data


def write_pickle(filename, data):
    """Write data in pickle file.

    See more at `pickle <https://docs.python.org/3/library/pickle.html>`_.

    Parameters
    ----------
    filename : str
        Full filename with path of file.
    data : dict
        Data to write in pickle file.

    """
    assert isinstance(filename, str)
    assert isinstance(data, dict)

    with open(filename, "wb") as f:
        pickle.dump(data, f)


def read_csv(filename, newline="", delimiter=",", quotechar='"', encoding="utf-8"):
    """Read in a CSV file.

    See more at `csv <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    filename : str
        Full filename with path of file.
    newline : str
        Newline character.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    reader
        Reader object, which can be iterated over.

    """
    assert isinstance(filename, str)
    assert isinstance(newline, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)
    assert isinstance(encoding, str)

    with open(filename, newline=newline, encoding=encoding) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        assert isinstance(csv_reader, csv.reader)
        return csv_reader


def write_csv(
    data, filename, newline="", delimiter=",", quotechar='"', encoding="utf-8"
):
    """Short summary.

    See more at `csv <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    data : list
        List of :class:`dict`. Key is column, value is cell content.
    filename : str
        Full filename with path of file.
    newline : str
        Newline character.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    """
    assert isinstance(data, list)
    assert isinstance(filename, str)
    assert isinstance(newline, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)
    assert isinstance(encoding, str)

    with open(filename, "w", newline=newline, encoding=encoding) as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in data:
            writer.writerow(row)


def read_csv_as_dicts(
    filename, newline="", delimiter=",", quotechar='"', encoding="utf-8"
):
    """Read in CSV file into a list of :class:`dict`.

    This offers an easy import functionality of your data from CSV files.
    See more at
    `csv <https://docs.python.org/3/library/csv.html>`_.

    CSV file structure:
    1) The header row contains the column names.
    2) A row contains one dataset
    3) A column contains one specific attribute.

    Recommendation: Name the column name the way you want the attribute to be
    named later in your Dataverse object. See the
    `pyDataverse templates <https://github.com/AUSSDA/pyDataverse_templates>`_
    for this. The created :class:`dict` can later be used for the `set()`
    function to create Dataverse objects.

    Parameters
    ----------
    filename : str
        Filename with full path.
    newline : str
        Newline character.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.
    encoding : str
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    list
        List with one :class:`dict` each row. The keys of a :class:`dict` are
        named after the columen names.

    """
    assert isinstance(filename, str)
    assert isinstance(newline, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)
    assert isinstance(encoding, str)

    with open(filename, "r", newline=newline, encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)
        data = []
        for row in reader:
            data.append(dict(row))
    assert isinstance(data, list)
    return data


def write_dicts_as_csv(data, fieldnames, filename, delimiter=",", quotechar='"'):
    """Write :class:`dict` to a CSV file

    This offers an easy export functionality of your data to a CSV files.
    See more at `csv <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    data : dict
        Dictionary with columns as keys, to be written in the CSV file.
    fieldnames : list
        Sequence of keys that identify the order of the columns.
    filename : str
        Filename with full path.
    delimiter : str
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : str
        Quote-character of CSV file. Defaults to '"'.

    """
    assert isinstance(data, str)
    assert isinstance(fieldnames, list)
    assert isinstance(filename, str)
    assert isinstance(delimiter, str)
    assert isinstance(quotechar, str)

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for d in data:
            for key, val in d.items():
                if isinstance(val, dict) or isinstance(val, list):
                    d[key] = json.dump(val)
            writer.writerow(d)


def clean_string(str):
    """Clean a string.

    Trims whitespace.

    Parameters
    ----------
    str : str
        String to be cleaned.

    Returns
    -------
    str
        Cleaned string.

    """
    assert isinstance(str, str)

    clean_str = str.strip()
    clean_str = clean_str.replace("  ", " ")

    assert isinstance(clean_str, str)
    return clean_str


def validate_data(data, filename_schema, file_format="json"):
    """Validate data against a schema.

    Parameters
    ----------
    data : dict
        Data to be validated.
    filename_schema : str
        Filename with full path of the schema file.
    file_format : str
        File format to be validated.

    Returns
    -------
    bool
        `True` if data was validated, `False` if not.

    """
    assert isinstance(data, dict)
    assert isinstance(filename_schema, str)
    assert isinstance(file_format, str)

    if file_format == "json":
        validate(instance=data, schema=read_json(filename_schema))
        return True
    elif file_format == "xml":
        print("INFO: Not implemented yet.")
        return False
    else:
        print("WARNING: No valid format passed.")
        return False


def create_dataverse_url(base_url, identifier):
    """Creates URL of Dataverse.

    Example: https://data.aussda.at/dataverse/autnes

    Parameters
    ----------
    base_url : str
        Base URL of Dataverse instance
    identifier : str
        Can either be a dataverse id (long), a dataverse alias (more
        robust), or the special value ``:root``.

    Returns
    -------
    str
        URL of the dataverse

    """
    assert isinstance(base_url, str)
    assert isinstance(identifier, str)

    base_url = base_url.rstrip("/")
    url = "{0}/dataverse/{1}".format(base_url, identifier)
    assert isinstance(url, str)
    return url


def create_dataset_url(base_url, identifier, is_pid):
    """Creates URL of Dataset.

    Example: https://data.aussda.at/dataset.xhtml?persistentId=doi:10.11587/CCESLK

    Parameters
    ----------
    base_url : str
        Base URL of Dataverse instance
    identifier : str
        Identifier of the dataset. Can be dataset id or persistent
        identifier of the dataset (e. g. doi).
    is_pid : bool
        ``True`` to use persistent identifier. ``False``, if not.

    Returns
    -------
    str
        URL of the dataset

    """
    assert isinstance(base_url, str)
    assert isinstance(identifier, str)
    assert isinstance(is_pid, bool)

    base_url = base_url.rstrip("/")
    if is_pid:
        url = "{0}/dataset.xhtml?persistentId={1}".format(base_url, identifier)
    else:
        url = "{0}/NOT-YET-IMPLEMENTED/{1}".format(base_url, identifier)
        assert isinstance(url, str)
    return url


def create_datafile_url(base_url, identifier, is_filepid):
    """Creates URL of Datafile.

    Example
    - File ID: https://data.aussda.at/file.xhtml?persistentId=doi:10.11587/CCESLK/5RH5GK

    Parameters
    ----------
    base_url : str
        Base URL of Dataverse instance
    identifier : str
        Identifier of the datafile. Can be datafile id or persistent
        identifier of the datafile (e. g. doi).
    is_filepid : bool
        ``True`` to use persistent identifier. ``False``, if not.

    Returns
    -------
    str
        URL of the datafile

    """
    assert isinstance(base_url, str)
    assert isinstance(identifier, str)

    base_url = base_url.rstrip("/")
    if is_filepid:
        url = "{0}/file.xhtml?persistentId={1}".format(base_url, identifier)
    else:
        url = "{0}/file.xhtml?fileId={1}".format(base_url, identifier)
    assert isinstance(url, str)
    return url
