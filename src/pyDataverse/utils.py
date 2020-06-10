# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dataverse utility functions."""
import csv
import json
from jsonschema import validate
import pickle


def read_file(filename, mode='r'):
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
    try:
        with open(filename, mode) as f:
            data = f.read()
        return data
    except IOError:
        print('An error occured trying to read the file {}.'.format(filename))
    except Exception as e:
        raise e


def write_file(filename, data, mode='w'):
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

    """
    try:
        with open(filename, mode) as f:
            f.write(data)
    except IOError:
        print('An error occured trying to write the file {}.'.format(filename))
    except Exception as e:
        raise e


def read_json(filename, mode='r', encoding='utf-8'):
    """Read in a json file.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    filename : string
        Filename with full path.

    Returns
    -------
    dict
        Data as a json-formatted string.

    """
    try:
        with open(filename, mode, encoding=encoding) as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise e


def write_json(filename, data, mode='w', encoding='utf-8'):
    """Write data to a json file.

    Parameters
    ----------
    filename : string
        Filename with full path.
    data : dict
        Data to be written in the json file.
    mode : string
        Write mode of file. Defaults to `w`. See more at
        https://docs.python.org/3/library/functions.html#open

    """
    try:
        with open(filename, mode, encoding=encoding) as f:
            json.dump(data, f, indent=2)
    except IOError:
        print('An error occured trying to write the file {}.'.format(filename))
    except Exception as e:
        raise e


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
    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            return data
    except Exception as e:
        raise e


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
    try:
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        raise e


def read_csv(filename):
    """Read in CSV file.

    See more at `csv.reader() <https://docs.python.org/3.5/library/csv.html>`_.

    Parameters
    ----------
    filename : string
        Full filename with path of file.

    Returns
    -------
    reader
        Reader object, which can be iterated over.

    """
    try:
        with open(filename, newline='') as csvfile:
            return csv.reader(csvfile, delimiter=',', quotechar='"')
    except Exception as e:
        raise e
    finally:
        csvfile.close()


def write_csv(data, filename, delimiter=',', quotechar='"'):
    """Short summary.

    Parameters
    ----------
    data : type
        Description of parameter `data`.
    filename : type
        Description of parameter `filename`.
    delimiter : type
        Description of parameter `delimiter` (the default is ';').
    quotechar : type
        Description of parameter `quotechar` (the default is '"').

    Returns
    -------
    type
        Description of returned object.

    Raises
    -------
    ExceptionName
        Why the exception is raised.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in data:
            writer.writerow(row)


def read_csv_as_dict(filename, delimiter=',', quotechar='"', encoding='utf-8'):
    """Read in csv file and convert it into a list of dicts.

    This offers an easy import functionality of csv files with dataset metadata.

    Assumptions:
    1) The header rows contains the column names, named after Dataverse's
    dataset attribute standard naming convention.
    2) One row contains one dataset

    After the import, the created dict then can directly be used to set
    Dataset() attributes via ``Dataset.set(data)``.

    Parameters
    ----------
    filename : string
        Filename with full path.
    delimiter : string
        Cell delimiter of CSV file. Defaults to ';'.
    quotechar : string
        Quote-character of CSV file. Defaults to '"'.
    encoding : string
        Character encoding of file. Defaults to 'utf-8'.

    Returns
    -------
    list
        List with one dict per row (=dataset). The keys of the dicts are named
        after the columen names, which must be named after the Dataverse
        dataset metadata naming convention.

    """
    with open(filename, 'r', newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter,
                                quotechar=quotechar)
        data = []
        for row in reader:
            data.append(dict(row))
    return data


def write_dict_as_csv(data, fieldnames, filename, delimiter=',', quotechar='"'):
    """Short summary.

    Parameters
    ----------
    data : type
        Description of parameter `data`.
    fieldnames : type
        Description of parameter `fieldnames`.
    filename : type
        Description of parameter `filename`.
    delimiter : type
        Description of parameter `delimiter` (the default is ';').
    quotechar : type
        Description of parameter `quotechar` (the default is '"').

    Returns
    -------
    type
        Description of returned object.

    Raises
    -------
    ExceptionName
        Why the exception is raised.

    Examples
    -------
    Examples should be written in doctest format, and
    should illustrate how to use the function/class.
    >>>

    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for d in data:
            for key, val in d.items():
                if isinstance(val, dict) or isinstance(val, list):
                    d[key] = json.dump(val)
            writer.writerow(d)


def tree_walker_count_types(children, num_dataverses=0, num_datasets=0, num_datafiles=0):
    """Count data types from Dataverse tree.

    Parameters
    ----------
    children : list
        List of child elements.
    num_dataverses : int
        Number of Dataverses in tree.
    num_datasets : int
        Number of Datasets in tree.
    num_datafiles : int
        Number of Datafiles in tree.

    Returns
    -------
    list
        [num_dataverses, num_datasets, num_datafiles]

    """
    for child in children:
        if child['type'] == 'dataverse':
            num_dataverses += 1
            num_dataverses, num_datasets, num_datafiles = count_tree_types(child['children'], num_dataverses, num_datasets, num_datafiles)
        elif child['type'] == 'dataset':
            num_datasets += 1
            num_dataverses, num_datasets, num_datafiles = count_tree_types(child['children'], num_dataverses, num_datasets, num_datafiles)
        elif child['type'] == 'datafile':
            num_datafiles += 1
    return num_dataverses, num_datasets, num_datafiles


def clean_string(str):
    clean_str = str.strip()
    clean_str = clean_str.replace('  ', ' ')
    return clean_str


def validate_data(data, filename_schema, format='json'):
    """Short summary.

    Parameters
    ----------
    format : type
        Description of parameter `format`.
    filename_schema : type
        Description of parameter `filename_schema`.

    Returns
    -------
    type
        Description of returned object.

    """
    if format == 'json':
        validate(instance=data, schema=read_json(filename_schema))
        return True
    elif format == 'xml':
        print('INFO: Not implemented yet.')
        return True
    else:
        print('ERROR: No valid format passed.')
        return False
