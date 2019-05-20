# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find out more at https://github.com/AUSSDA/pyDataverse."""
import json


def json_to_dict(data):
    """Convert JSON to a dict().

    See more about the json module at
    https://docs.python.org/3.5/library/json.html

    Parameters
    ----------
    data : string
        Data as a json-formatted string.

    Returns
    -------
    dict
        Data as Python Dictionary.

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
        Data as Python Dictionary.

    Returns
    -------
    string
        Data as a json-formatted string.

    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        raise e


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


def read_file_json(filename):
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
        return json.loads(read_file(filename, 'r'))
    except Exception as e:
        raise e


def write_file_json(filename, data, mode='w'):
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
    write_file(filename, dict_to_json(data), mode)
