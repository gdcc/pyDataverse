# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pipeline functionalities."""
from datetime import datetime
import json
import os
from pyDataverse.api import NativeApi
from pyDataverse.utils import clean_string
from pyDataverse.utils import read_csv_as_dict
from pyDataverse.utils import read_json
from pyDataverse.utils import write_json
from pyDataverse.utils import write_pickle
from pyDataverse.models import Datafile
from pyDataverse.models import Dataset
from pyDataverse.models import Dataverse
import time


def get_pipeline_config(filename_config):
    """Short summary.

    Parameters
    ----------
    filename_config : type
        Description of parameter `filename_config`.

    Returns
    -------
    type
        Description of returned object.

    """
    config = read_json(filename_config)
    print('- Load config COMPLETED.')
    return config


def save_pickle(seq, data):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.
    data : type
        Description of parameter `data`.

    Returns
    -------
    type
        Description of returned object.

    """
    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']

    write_pickle(os.path.join(seq_cfg['filename']), data)
    print('- Save Pickle COMPLETED.')


def get_num_iterations(seq):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.

    Returns
    -------
    type
        Description of returned object.

    """

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']

    if 'num_iterations' in global_cfg:
        if global_cfg['num_iterations']:
            num_iterations = global_cfg['num_iterations']
        else:
            num_iterations = seq_cfg['num_iterations']
    elif 'num_iterations' in seq_cfg:
        num_iterations = seq_cfg['num_iterations']
    else:
        print('ERROR: No number of iterations available.')
    return num_iterations


def import_dataverses(seq):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.

    Returns
    -------
    type
        Description of returned object.

    """
    dv_lst = []
    dv_idx = {}
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']

    if seq_cfg['file_type'] == 'csv':
        mapping = read_json(os.path.join(seq_cfg['mapping_file']))['dataverse']
        dataverses = read_csv_as_dict(seq_cfg['filename'], delimiter=seq_cfg['file_format']['delimiter'])

        for dv in dataverses:
            dv_tmp = {}
            counter += 1

            for key, val in dv.items():
                # only import empty cells and if in mapping file
                if val and key in mapping:
                    # convert bool values
                    if mapping[key]['type'] == 'boolean':
                        if val == seq_cfg['file_format']['boolean_true']:
                            val = True
                        elif val == seq_cfg['file_format']['boolean_false']:
                            val = False
                    elif mapping[key]['type'] == 'string':
                        val = clean_string(val)
                        if 'format' in mapping[key]:
                            if mapping[key]['format'] == 'json':
                                val = json.loads(val)
                    dv_tmp[mapping[key]['target']] = val
            dv = Dataverse()
            dv.set(dv_tmp)
            dv_lst.append(dv)
            dv_idx[dv.dataverse_id] = len(dv_lst)
            num_iterations = get_num_iterations(seq)
            if counter >= num_iterations and num_iterations >= 0:
                break
    print('- Import Dataverses COMPLETED.')
    return dv_lst, dv_idx


def create_dataverses_json(seq, dv_lst):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.
    dv_lst : type
        Description of parameter `dv_lst`.

    Returns
    -------
    type
        Description of returned object.

    """
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']

    for dv in dv_lst:
        write_json(os.path.join(seq_cfg['folder_path'], '{0}_dataverse.json'.format(dv.dataverse_id)), dv.dict())
        num_iterations = get_num_iterations(seq)
        if counter >= num_iterations and num_iterations >= 0:
            break
        counter += 1
    print('- Create Dataverses JSON COMPLETED.')


def create_datafiles_json(seq, df_lst):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.
    df_lst : type
        Description of parameter `df_lst`.

    Returns
    -------
    type
        Description of returned object.

    """
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    for df in df_lst:
        num_iterations = get_num_iterations(seq)
        if counter >= num_iterations and num_iterations >= 0:
            break
    print('- Create Datafiles JSON COMPLETED.')


def import_datafiles(seq):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.

    Returns
    -------
    type
        Description of returned object.

    """
    df_lst = []
    df_idx = {}
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']

    if seq_cfg['file_type'] == 'csv':
        mapping = read_json(os.path.join(seq_cfg['mapping_file']))['datafile']
        datafiles = read_csv_as_dict(seq_cfg['filename'], delimiter=seq_cfg['file_format']['delimiter'])

        for df in datafiles:
            df_tmp = {}
            df_id = None
            # only import empty cells
            for key, val in df.items():
                if val and key in mapping:
                    # convert bool values
                    if mapping[key]['type'] == 'boolean':
                        if val == seq_cfg['file_format']['boolean_true']:
                            val = True
                        elif val == seq_cfg['file_format']['boolean_false']:
                            val = False
                    elif mapping[key]['type'] == 'string':
                        val = clean_string(val)
                        if 'format' in mapping[key]:
                            if mapping[key]['format'] == 'json':
                                val = json.loads(val)
                    df_tmp[mapping[key]['target']] = val
            df = Datafile()
            df.set(df_tmp)
            df_lst.append(df)
            df_idx[df.datafile_id] = len(df_lst)
            num_iterations = get_num_iterations(seq)
            if counter >= num_iterations and num_iterations >= 0:
                break
    print('- Import Datafiles COMPLETED.')
    return df_lst, df_idx


# def create_dv_tree(dataverses=None, datasets=None, datafiles=None):
#     dv_tree = []
#     if dataverses:
#         # TODO: check if sub-dataverses and create tree structure out of flat list
#         dv_tree = dataverses[0]
#     if datasets:
#         if dataverses:
#             for ds in datasets[0]:
#                 dv_tree[dv_idx[ds.dataverse_id]]['datasets'].append(ds)
#         else:
#             dv_tree = datasets[0]
#     if datafiles:
#         if datasets:
#             for df in datafiles[0]:
#                 dv_tree[dv_idx[ds.dataverse_id]]['datasets'].append(ds)
#         else:
#             dv_tree = datafiles[0]
#     return dv_tree


def create_dataverses(seq, dv_lst):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.
    dv_lst : type
        Description of parameter `dv_lst`.

    Returns
    -------
    type
        Description of returned object.

    """
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']
    user = seq_cfg['instance']['user']
    instance = seq_cfg['instance']['instance_name']
    base_url = config['instances'][instance]['base_url']
    api_token = config['instances'][instance]['user'][user]['api_token']
    api = NativeApi(base_url, api_token)

    for dv in dv_lst:
        do_upload = True
        if do_upload:
            try:
                resp = api.create_dataverse(dv.alias, dv.to_json(), parent=dv.dataverse)
                if 'status' in resp.json():
                    if resp.json()['status'] == 'OK':
                        if 'data' not in resp.json():
                            print('ERROR: Create Dataverse {0} - no \'data\' in API response.'.format(dv.alias))
                    else:
                        print('ERROR: Create Dataverse {0} API Request Status not OK'.format(dv.alias))
                else:
                    print('ERROR: Create Dataverse {0} API Request not working.'.format(dv.alias))
            except:
                print('Dataverse {0} could not be created.'.format(dv.alias))
            time.sleep(config['instances'][instance]['wait_time']['default'])
        else:
            pass
        num_iterations = get_num_iterations(seq)
        if counter >= num_iterations and num_iterations >= 0:
            break
        counter += 1
    print('- Create Dataverses COMPLETED.')


def delete_dataverses(seq, dv_lst):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.
    dv_lst : type
        Description of parameter `dv_lst`.

    Returns
    -------
    type
        Description of returned object.

    """
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']
    user = seq_cfg['instance']['user']
    instance = seq_cfg['instance']['instance_name']

    base_url = config['instances'][instance]['base_url']
    api_token = config['instances'][instance]['user'][user]['api_token']
    api = NativeApi(base_url, api_token)

    for dv in dv_lst:
        do_deletion = True
        if do_deletion:
            try:
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                resp = api.delete_dataverse(dv.alias)
                if 'status' in resp.json():
                    if resp.json()['status'] == 'OK':
                        if 'data' not in resp.json():
                            print('ERROR: Delete Dataverse {0} - no data in API response.'.format(dv.alias))
                    else:
                        print('ERROR: Delete Dataverse {0} - API request status not OK.'.format(dv.alias))
            except:
                print('Dataverse \'{0}\' could not be deleted.'.format(dv.alias))
            time.sleep(config['instances'][instance]['wait_time']['default'])
        else:
            print('Dataverse {0} can not be deleted.'.format(dv.alias))
        num_iterations = get_num_iterations(seq)
        if counter >= num_iterations and num_iterations >= 0:
            break
        counter += 1
    print('- Delete Dataverses COMPLETED.')


def publish_dataverses(seq, dv_lst):
    """Short summary.

    Parameters
    ----------
    seq : type
        Description of parameter `seq`.
    dv_lst : type
        Description of parameter `dv_lst`.

    Returns
    -------
    type
        Description of returned object.

    """
    counter = 0

    config = get_pipeline_config(os.environ['PIPELINE_CONFIG'])
    seq_cfg = config['pipeline']['sequence'][seq]['settings']
    global_cfg = config['pipeline']['global']
    user = seq_cfg['instance']['user']
    instance = seq_cfg['instance']['instance_name']

    base_url = config['instances'][instance]['base_url']
    api_token = config['instances'][instance]['user'][user]['api_token']
    api = NativeApi(base_url, api_token)

    for dv in dv_lst:
        do_publish = True
        if do_publish:
            try:
                resp = api.publish_dataverse(dv.alias)
                if 'status' in resp.json():
                    if resp.json()['status'] == 'OK':
                        if 'data' not in resp.json():
                            print('ERROR: Publish Dataverse {0} - no data in API response.'.format(dv.alias))
                    else:
                        print('ERROR: Publish Dataverse {0} API request status not OK.'.format(dv.alias))
            except:
                print('Dataverse {0} could not be published.'.format(dv.alias))
            time.sleep(1)
        else:
            print('Dataverse {0} can not be published.'.format(dv.alias))
        num_iterations = get_num_iterations(seq)
        if counter >= num_iterations and num_iterations >= 0:
            break
        counter += 1
    print('- Publish Dataverses COMPLETED.')
