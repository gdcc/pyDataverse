# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper functions."""
import csv
import json
from jsonschema import validate
import pickle


def read_file(filename, mode='r', encoding='utf-8'):
    """Read in a file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    mode : string
        Read mode of file. Defaults to `r`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    Returns
    -------
    string
        Returns data as string.

    """
    with open(filename, mode, encoding=encoding) as f:
        data = f.read()
    return data


def write_file(filename, data, mode='w', encoding='utf-8'):
    """Write data in a file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    data : string
        Data to be stored.
    mode : string
        Read mode of file. Defaults to `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    """
    with open(filename, mode, encoding=encoding) as f:
        f.write(data)


def read_json(filename, mode='r', encoding='utf-8'):
    """Read in a json file.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    filename : string
        Filename with full path.
    mode : string
        Read mode of file. Defaults to `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    dict
        Data as a json-formatted string.

    """
    with open(filename, mode, encoding=encoding) as f:
        data = json.load(f)
    return data


def write_json(filename, data, mode='w', encoding='utf-8'):
    """Write data to a json file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    data : dict
        Data to be written in the JSON file.
    mode : string
        Write mode of file. Defaults to `w`. See more at
        https://docs.python.org/3/library/functions.html#open
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    """
    with open(filename, mode, encoding=encoding) as f:
        json.dump(data, f, indent=2)


def read_pickle(filename):
    """Read in pickle file.

    See more at `pickle <https://docs.python.org/3/library/pickle.html>`_.

    Parameters
    ----------
    filename : string
        Full filename with path of file.

    Returns
    -------
    data
        Data object.

    """
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        return data


def write_pickle(filename, data):
    """Write data in pickle file.

    See more at `pickle <https://docs.python.org/3/library/pickle.html>`_.

    Parameters
    ----------
    filename : string
        Full filename with path of file.
    data : object
        Data to write in pickle file.

    """
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def read_csv(filename, newline='', delimiter=',', quotechar='"',
             encoding='utf-8'):
    """Read in a CSV file.

    See more at `csv.reader() <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    filename : string
        Full filename with path of file.
    newline : string
        Newline character.
    delimiter : string
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : string
        Quote-character of CSV file. Defaults to '"'.
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    reader
        Reader object, which can be iterated over.

    """
    with open(filename, newline=newline, encoding=encoding) as csvfile:
        return csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)


def write_csv(data, filename, newline='', delimiter=',', quotechar='"',
              encoding='utf-8'):
    """Short summary.

    See more at `csv.reader() <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    data : list
        List of :class:`dict`s. Key is column, value is cell content.
    filename : string
        Full filename with path of file.
    newline : string
        Newline character.
    delimiter : string
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : string
        Quote-character of CSV file. Defaults to '"'.
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    """
    with open(filename, 'w', newline=newline, encoding=encoding) as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in data:
            writer.writerow(row)


def read_csv_as_dict(filename, newline='', delimiter=',', quotechar='"',
                     encoding='utf-8'):
    """Read in CSV file into a list of :class:`dict`s.

    This offers an easy import functionality of your data from CSV files.
    See more at `csv.reader() <https://docs.python.org/3/library/csv.html>`_.

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
    filename : string
        Filename with full path.
    newline : string
        Newline character.
    delimiter : string
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : string
        Quote-character of CSV file. Defaults to '"'.
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    list
        List with one :class:`dict` each row. The keys of a :class:`dict` are
        named after the columen names.

    """
    with open(filename, 'r', newline=newline, encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter,
                                quotechar=quotechar)
        data = []
        for row in reader:
            data.append(dict(row))
    return data


def write_dict_as_csv(data, fieldnames, filename, delimiter=',', quotechar='"'):
    """Write :class:`dict` to a CSV file

    This offers an easy export functionality of your data to a CSV files.
    See more at `csv.reader() <https://docs.python.org/3/library/csv.html>`_.

    Parameters
    ----------
    data : type
        Description of parameter `data`.
    fieldnames : list
        Sequence of keys that identify the order of the columns.
    filename : string
        Filename with full path.
    delimiter : string
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : string
        Quote-character of CSV file. Defaults to '"'.

    """
    with open(filename, 'w', newline='') as csvfile:
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
    str : string
        String to be cleaned.

    Returns
    -------
    string
        Cleaned string.

    """
    clean_str = str.strip()
    clean_str = clean_str.replace('  ', ' ')
    return clean_str


def validate_data(data, filename_schema, format='json'):
    """Validate data against a schema.

    Parameters
    ----------
    data : dict
        Data to be validated.
    filename_schema : string
        Filename with full path of the schema file.
    format : string
        Data format of file to be validated.

    Returns
    -------
    bool
        `True` if data was validated, `False` if not.

    """
    if format == 'json':
        validate(instance=data, schema=read_json(filename_schema))
        return True
    elif format == 'xml':
        print('INFO: Not implemented yet.')
        return False
    else:
        print('WARNING: No valid format passed.')
        return False


def create_dataverse_url(base_url, identifier):
    """Creates URL of Dataverse.

    Example: https://data.aussda.at/dataverse/autnes

    Parameters
    ----------
    base_url : str
        Base URL of Dataverse instance
    identifier : string
        Can either be a dataverse id (long), a dataverse alias (more
        robust), or the special value ``:root``.

    Returns
    -------
    str
        URL of the dataverse

    """
    base_url = base_url.rstrip('/')
    return '{0}/dataverse/{1}'.format(base_url, identifier)


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
    base_url = base_url.rstrip('/')
    if is_pid:
        url = '{0}/dataset.xhtml?persistentId={1}'.format(base_url, identifier)
    else:
        url = '{0}/NOT-YET-IMPLEMENTED/{1}'.format(base_url, identifier)
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
    base_url = base_url.rstrip('/')
    if is_filepid:
        url = '{0}/file.xhtml?persistentId={1}'.format(base_url, identifier)
    else:
        url = '{0}/file.xhtml?fileId={1}'.format(base_url, identifier)
    return url
