from __future__ import absolute_import

import csv
import json


def json_to_dict(data):
    """Convert json to a python dict()."""
    return json.loads(data)


def dict_to_json(data):
    """Convert python dict() to json."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def read_file(filename):
    """Read in a file."""
    try:
        with open(filename) as f:
            data = f.read()
        return data
    except Exception as e:
        raise e


def read_json_file(filename):
    """Read in a json file."""
    return json.loads(read_file(filename))


def read_csv(filename):
    """Read in a csv file."""
    with open(filename, newline='') as csvfile:
        return csv.reader(csvfile, delimiter=',', quotechar='"')


def read_datasets_csv(filename):
    """Read in datasets from a CSV file with doi and dataverse.

    Dataverse must be a alias or an id.
    """
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(reader, None)
        dataset_list = []
        for row in reader:
            dataset_list.append({
                'doi': row[0],
                'dataverse': row[1]
            })
    return dataset_list


def write_file(filename, string, type='w'):
    """Write a file."""
    with open(filename, type) as f:
        f.write(string)


def write_json_file(filename, data, type='w'):
    """Write a json file."""
    write_file(filename, dict_to_json(data))


def write_datasets_csv(filename):
    """Write a datasets csv file with doi and related dataverse."""
    with open(filename, 'w', newline='') as csvfile:
        return csv.writer(csvfile, delimiter=',', quotechar='"')
