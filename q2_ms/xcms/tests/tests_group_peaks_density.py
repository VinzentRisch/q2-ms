import os
from shutil import copytree

import pandas as pd
from qiime2.plugin.testing import TestPluginBase

from q2_ms.types import XCMSExperimentDirFmt
from q2_ms.xcms.group_peaks_density import group_peaks_density


class TestGroupPeaksDensity(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def test_group_peaks_density(self):
        xcms_experiment = XCMSExperimentDirFmt()
        copytree(
            self.get_data_path("xcms_experiment_peaks"),
            str(xcms_experiment),
            dirs_exist_ok=True,
        )
        xcms_experiment_features = group_peaks_density(
            xcms_experiment=xcms_experiment,
            bw=31,
            min_fraction=0.4,
            min_samples=1,
            bin_size=0.3,
            max_features=100,
            ppm=0.1,
            sample_metadata_column="sample_group",
        )
        features_exp = pd.read_csv(
            self.get_data_path(
                "xcms_experiment_features/xcms_experiment_feature_definitions.txt"
            ),
            sep="\t",
            index_col=0,
        )
        features_obs = pd.read_csv(
            os.path.join(
                str(xcms_experiment_features), "xcms_experiment_feature_definitions.txt"
            ),
            sep="\t",
            index_col=0,
        )
        pd.testing.assert_frame_equal(features_exp, features_obs)
