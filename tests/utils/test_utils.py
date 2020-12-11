from pyDataverse.utils import read_json, save_tree_data, dataverse_tree_walker
from ..conftest import test_config


class TestUtilsSaveTreeData:
    def test_dataverse_tree_walker_valid_default(self):
        dv_ids = [1, 2, 3]
        dv_aliases = ["parent_dv_1", "parent_dv_1_sub_dv_1", "parent_dv_2"]
        ds_ids = ["1AB23C", "4DE56F", "7GH89I", "0JK1LM", "2NO34P"]
        ds_pids = [
            "doi:12.34567/1AB23C",
            "doi:12.34567/4DE56F",
            "doi:12.34567/7GH89I",
            "doi:12.34567/0JK1LM",
            "doi:12.34567/2NO34P",
        ]
        df_ids = [1, 2, 3, 4, 5, 6, 7]
        df_filenames = [
            "appendix.pdf",
            "survey.zsav",
            "manual.pdf",
            "study.zsav",
            "documentation.pdf",
            "data.R",
            "summary.md",
        ]
        df_labels = [
            "appendix.pdf",
            "survey.zsav",
            "manual.pdf",
            "study.zsav",
            "documentation.pdf",
            "data.R",
            "summary.md",
        ]
        df_pids = [
            "doi:12.34567/1AB23C/ABC123",
            "doi:12.34567/1AB23C/DEF456",
            "doi:12.34567/4DE56F/GHI789",
            "doi:12.34567/7GH89I/JKL012",
            "doi:12.34567/0JK1LM/MNO345",
            "doi:12.34567/0JK1LM/PQR678",
            "doi:12.34567/2NO34P/STU901",
        ]

        data = read_json(test_config["tree_filename"])
        dataverses, datasets, datafiles = dataverse_tree_walker(data)

        assert isinstance(dataverses, list)
        assert isinstance(datasets, list)
        assert isinstance(datafiles, list)
        assert len(dataverses) == 3
        assert len(datasets) == 5
        assert len(datafiles) == 7

        for dv in dataverses:
            assert "dataverse_alias" in dv
            assert "dataverse_id" in dv
            assert dv["dataverse_alias"] in dv_aliases
            dv_aliases.pop(dv_aliases.index(dv["dataverse_alias"]))
            assert dv["dataverse_id"] in dv_ids
            dv_ids.pop(dv_ids.index(dv["dataverse_id"]))
        assert (len(dv_aliases)) == 0
        assert (len(dv_ids)) == 0

        for ds in datasets:
            assert "dataset_id" in ds
            assert "pid" in ds
            assert ds["dataset_id"] in ds_ids
            ds_ids.pop(ds_ids.index(ds["dataset_id"]))
            assert ds["pid"] in ds_pids
            ds_pids.pop(ds_pids.index(ds["pid"]))
        assert (len(ds_ids)) == 0
        assert (len(ds_pids)) == 0

        for df in datafiles:
            assert "datafile_id" in df
            assert "filename" in df
            assert "label" in df
            assert "pid" in df
            assert df["datafile_id"] in df_ids
            df_ids.pop(df_ids.index(df["datafile_id"]))
            assert df["filename"] in df_filenames
            df_filenames.pop(df_filenames.index(df["filename"]))
            assert df["label"] in df_labels
            df_labels.pop(df_labels.index(df["label"]))
            assert df["pid"] in df_pids
            df_pids.pop(df_pids.index(df["pid"]))
        assert (len(df_ids)) == 0
        assert (len(df_filenames)) == 0
        assert (len(df_pids)) == 0
