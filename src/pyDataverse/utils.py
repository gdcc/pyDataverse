"""Helper functions."""

import csv
import json
import os
import pickle

from jsonschema import validate


CSV_JSON_COLS = [
    "otherId",
    "series",
    "author",
    "dsDescription",
    "subject",
    "keyword",
    "topicClassification",
    "language",
    "grantNumber",
    "dateOfCollection",
    "kindOfData",
    "dataSources",
    "otherReferences",
    "contributor",
    "relatedDatasets",
    "relatedMaterial",
    "datasetContact",
    "distributor",
    "producer",
    "publication",
    "software",
    "timePeriodCovered",
    "geographicUnit",
    "geographicBoundingBox",
    "geographicCoverage",
    "socialScienceNotes",
    "unitOfAnalysis",
    "universe",
    "targetSampleActualSize",
    "categories",
]


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


def read_json(filename: str, mode: str = "r", encoding: str = "utf-8") -> dict:
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
    # TODO: add kwargs
    with open(filename, mode, encoding=encoding) as f:
        data = json.load(f)

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
    filename,
    newline="",
    delimiter=",",
    quotechar='"',
    encoding="utf-8",
    remove_prefix=True,
    prefix="dv.",
    json_cols=CSV_JSON_COLS,
    false_values=["FALSE"],
    true_values=["TRUE"],
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
    `pyDataverse templates <https://github.com/GDCC/pyDataverse_templates>`_
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

    data_tmp = []
    for ds in data:
        ds_tmp = {}
        for key, val in ds.items():
            if val in false_values:
                ds_tmp[key] = False
                ds_tmp[key] = True
            elif val in true_values:
                ds_tmp[key] = True
            else:
                ds_tmp[key] = val

        data_tmp.append(ds_tmp)
    data = data_tmp

    if remove_prefix:
        data_tmp = []
        for ds in data:
            ds_tmp = {}
            for key, val in ds.items():
                if key.startswith(prefix):
                    ds_tmp[key[len(prefix) :]] = val
                else:
                    ds_tmp[key] = val
            data_tmp.append(ds_tmp)
        data = data_tmp

    if len(json_cols) > 0:
        data_tmp = []
        for ds in data:
            ds_tmp = {}
            for key, val in ds.items():
                if key in json_cols:
                    ds_tmp[key] = json.loads(val)
                else:
                    ds_tmp[key] = val
            data_tmp.append(ds_tmp)
        data = data_tmp

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


def clean_string(string):
    """Clean a string.

    Trims whitespace.

    Parameters
    ----------
    str : str
        String to be cleaned.

    Returns
    -------
    string
        Cleaned string.

    """
    assert isinstance(string, str)

    clean_str = string.strip()
    clean_str = clean_str.replace("  ", " ")

    assert isinstance(clean_str, str)
    return clean_str


def validate_data(data: dict, filename_schema: str, file_format: str = "json") -> bool:
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
        url = "{0}/dataset.xhtml?id{1}".format(base_url, identifier)
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


def dataverse_tree_walker(
    data: list,
    dv_keys: list = ["dataverse_id", "dataverse_alias"],
    ds_keys: list = ["dataset_id", "pid"],
    df_keys: list = ["datafile_id", "filename", "pid", "label"],
) -> tuple:
    """Walk through a Dataverse tree by get_children().

    Recursively walk through the tree structure returned by ``get_children()``
    and extract the keys needed.

    Parameters
    ----------
    data : dict
        Tree data structure returned by ``get_children()``.
    dv_keys : list
        List of keys to be extracted from each Dataverse element.
    ds_keys : list
        List of keys to be extracted from each Dataset element.
    df_keys : list
        List of keys to be extracted from each Datafile element.

    Returns
    -------
    tuple
        (List of Dataverse, List of Datasets, List of Datafiles)
    """
    dataverses = []
    datasets = []
    datafiles = []

    if isinstance(data, list):
        for elem in data:
            dv, ds, df = dataverse_tree_walker(elem)
            dataverses += dv
            datasets += ds
            datafiles += df
    elif isinstance(data, dict):
        if data["type"] == "dataverse":
            dv_tmp = {}
            for key in dv_keys:
                if key in data:
                    dv_tmp[key] = data[key]
            dataverses.append(dv_tmp)
        elif data["type"] == "dataset":
            ds_tmp = {}
            for key in ds_keys:
                if key in data:
                    ds_tmp[key] = data[key]
            datasets.append(ds_tmp)
        elif data["type"] == "datafile":
            df_tmp = {}
            for key in df_keys:
                if key in data:
                    df_tmp[key] = data[key]
            datafiles.append(df_tmp)
        if "children" in data:
            if len(data["children"]) > 0:
                dv, ds, df = dataverse_tree_walker(data["children"])
                dataverses += dv
                datasets += ds
                datafiles += df
    return dataverses, datasets, datafiles


def save_tree_data(
    dataverses: list,
    datasets: list,
    datafiles: list,
    filename_dv: str = "dataverses.json",
    filename_ds: str = "datasets.json",
    filename_df: str = "datafiles.json",
    filename_md: str = "metadata.json",
) -> None:
    """Save lists from data returned by ``dv_tree_walker``.

    Collect lists of Dataverses, Datasets and Datafiles and save them in separated JSON files.

    Parameters
    ----------
    data : dict
        Tree data structure returned by ``get_children()``.
    filename_dv : str
        Filename with full path for the Dataverse JSON file.
    filename_ds : str
        Filename with full path for the Dataset JSON file.
    filename_df : str
        Filename with full path for the Datafile JSON file.
    filename_md : str
        Filename with full path for the metadata JSON file.
    """
    if os.path.isfile(filename_dv):
        os.remove(filename_dv)
    if os.path.isfile(filename_ds):
        os.remove(filename_ds)
    if os.path.isfile(filename_df):
        os.remove(filename_df)
    if len(dataverses) > 0:
        write_json(filename_dv, dataverses)
    if len(datasets) > 0:
        write_json(filename_ds, datasets)
    if len(datafiles) > 0:
        write_json(filename_df, datafiles)
    metadata = {
        "dataverses": len(dataverses),
        "datasets": len(datasets),
        "datafiles": len(datafiles),
    }
    write_json(filename_md, metadata)
    print(f"- Dataverses: {len(dataverses)}")
    print(f"- Datasets: {len(datasets)}")
    print(f"- Datafiles: {len(datafiles)}")
