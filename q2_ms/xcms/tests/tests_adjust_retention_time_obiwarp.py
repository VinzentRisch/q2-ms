import os
from shutil import copytree

import pandas as pd
from qiime2.plugin.testing import TestPluginBase

from q2_ms.types import XCMSExperimentDirFmt, mzMLDirFmt
from q2_ms.xcms.adjust_retention_time_obiwarp import (
    _validate_parameters,
    adjust_retention_time_obiwarp,
)


class TestAdjustRetentionTimeObiwarp(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def test_adjust_retention_time_obiwarp(self):
        xcms_experiment = XCMSExperimentDirFmt()
        copytree(
            self.get_data_path("xcms_experiment_read_in"),
            str(xcms_experiment),
            dirs_exist_ok=True,
        )
        spectra = mzMLDirFmt()
        copytree(self.get_data_path("faahKO"), str(spectra), dirs_exist_ok=True)
        xcms_experiment_rt_corrected = adjust_retention_time_obiwarp(
            spectra=spectra,
            xcms_experiment=xcms_experiment,
            bin_size=0.6,
            response=3,
            dist_fun="cor",
            gap_init=0.4,
            gap_extend=2.5,
            factor_diag=3,
            factor_gap=2,
            local_alignment=True,
            init_penalty=0.1,
            sample_metadata_column="sample_type",
            subset_label="QC",
            subset_adjust="previous",
            rtime_difference_threshold=6,
            chunk_size=1,
            threads=1,
        )
        rt_corrected_exp = pd.read_csv(
            self.get_data_path("rt_correction_R/rt_corrected.txt"),
            sep="\t",
        )["rtime_adjusted"]
        rt_corrected_obs = pd.read_csv(
            os.path.join(str(xcms_experiment_rt_corrected), "ms_backend_data.txt"),
            sep="\t",
            skiprows=1,
            index_col=0,
        )["rtime_adjusted"].reset_index(drop=True)
        self.assertTrue(rt_corrected_exp.equals(rt_corrected_obs))

    def test_invalid_combination_of_subset_parameters(self):
        with self.assertRaisesRegex(ValueError, r"combination"):
            _validate_parameters(True, False, True, True, False)
        with self.assertRaisesRegex(ValueError, r"combination"):
            _validate_parameters(True, True, False, True, False)
        with self.assertRaisesRegex(ValueError, r"combination"):
            _validate_parameters(False, True, True, True, False)

    def test_valid_mixed_subset_parameters(self):
        try:
            _validate_parameters(True, True, True, True, False)
            _validate_parameters(False, False, False, True, False)
        except ValueError:
            self.fail("_validate_parameters raised ValueError unexpectedly!")

    def test_init_penalty_without_local_alignment(self):
        with self.assertRaisesRegex(
            ValueError, r"--p-init-penalty.*--p-local-alignment"
        ):
            _validate_parameters(True, True, True, False, True)
