# coding: utf-8
from __future__ import absolute_import

import csv
import json


def json_to_dict(data):
    """Convert JSON to a dict().

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    data : string
        `data` as JSON-formatted string.

    Returns
    -------
    dict
        `data` represented as dict().

    """
    try:
        return json.loads(data)
    except Exception as e:
        raise e


def dict_to_json(data):
    """Convert dict() to JSON-formatted string.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    data : dict
        `data` represented as dict().

    Returns
    -------
    string
        `data` as JSON-formatted string

    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        raise e


def read_file(filename, mode='r'):
    """Read in data from a file.

    Parameters
    ----------
    filename : type
        Description of parameter `filename`.
    mode : string
        Read mode of file. Default is `r`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    Returns
    -------
    string
        Returns the whole content as string.

    """
    try:
        with open(filename, mode) as f:
            data = f.read()
        return data
    except Exception as e:
        raise e


def write_file(filename, string, mode='w'):
    """Write data in a file.

    Parameters
    ----------
    filename : string
        Full filename with path of file.
    string : string
        String of data to be written.
    mode : string
        Read mode of file. Default is `w`. See more at
        https://docs.python.org/3.5/library/functions.html#open

    """
    try:
        with open(filename, mode) as f:
            f.write(string)
    except Exception as e:
        raise e


def read_file_json(filename):
    """Read in JSON file.

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    filename : string
        Full filename with path of file.

    Returns
    -------
    dict
        Data represented as a dict().

    """
    try:
        return json.loads(read_file(filename), 'r')
    except Exception as e:
        raise e


def write_file_json(filename, data, mode='w'):
    """Write dict() in a JSON file.

    Parameters
    ----------
    filename : string
        Full filename with path of file.
    data : dict
        Data to be written in the JSON file.
    mode : string
        Write mode of file. Default is `w`. See more at
        https://docs.python.org/3/library/functions.html#open

    """
    write_file(filename, dict_to_json(data), mode)


def read_file_csv(filename):
    """Read in CSV file.

    See more about csv.reader() at https://docs.python.org/3.5/library/csv.html

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
