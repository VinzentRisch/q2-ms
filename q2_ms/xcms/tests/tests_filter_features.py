import os
from shutil import copytree

import pandas as pd
from qiime2.plugin.testing import TestPluginBase

from q2_ms.types import XCMSExperimentDirFmt
from q2_ms.xcms.filter_features import filter_features, validate_parameters


class TestValidateFilterParameters(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def test_invalid_parameter_combination(self):
        with self.assertRaisesRegex(
            ValueError,
            "The parameter 'blank_label' cannot be used in combination with the filter "
            "'rsd'",
        ):
            validate_parameters(filter="rsd", blank_label="blank")

    def test_invalid_parameter_combination_percent_missing(self):
        with self.assertRaisesRegex(
            ValueError,
            "combination or not at all.",
        ):
            validate_parameters(filter="percent-missing", qc_label="QC")


class TestFilterFeatures(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def setUp(self):
        super().setUp()

        self.xcms_experiment = XCMSExperimentDirFmt()
        copytree(
            self.get_data_path("xcms_experiment_filtering"),
            str(self.xcms_experiment),
            dirs_exist_ok=True,
        )

    def test_filter_features_rsd(self):
        xcms_experiment_filtered = filter_features(
            xcms_experiment=self.xcms_experiment,
            filter="rsd",
            threshold=0.4,
            qc_label="QC",
            sample_metadata_column="sampletype",
            na_rm=True,
            mad=False,
        )
        self._compare_features(xcms_experiment_filtered, "rsd")

    def test_filter_features_d_ratio(self):
        xcms_experiment_filtered = filter_features(
            xcms_experiment=self.xcms_experiment,
            filter="d_ratio",
            threshold=0.4,
            qc_label="QC",
            study_label="study",
            sample_metadata_column="sampletype",
            na_rm=True,
            mad=False,
        )
        self._compare_features(xcms_experiment_filtered, "d_ratio")

    def test_filter_features_percent_missing_exclude(self):
        xcms_experiment_filtered = filter_features(
            xcms_experiment=self.xcms_experiment,
            filter="percent_missing",
            threshold=40,
            exclude=True,
            qc_label="WT",
            sample_metadata_column="samplegroup",
        )
        self._compare_features(xcms_experiment_filtered, "percent_missing_exclude")

    def test_filter_features_percent_missing_include(self):
        xcms_experiment_filtered = filter_features(
            xcms_experiment=self.xcms_experiment,
            filter="percent_missing",
            threshold=40,
            exclude=False,
            qc_label="QC",
            sample_metadata_column="sampletype",
        )
        self._compare_features(xcms_experiment_filtered, "percent_missing_include")

    def test_filter_features_percent_missing_default(self):
        xcms_experiment_filtered = filter_features(
            xcms_experiment=self.xcms_experiment,
            filter="percent_missing",
            threshold=40,
            sample_metadata_column="samplegroup",
        )
        self._compare_features(xcms_experiment_filtered, "percent_missing_default")

    def test_filter_features_blank_flag(self):
        xcms_experiment_filtered = filter_features(
            xcms_experiment=self.xcms_experiment,
            filter="blank_flag",
            threshold=2,
            qc_label="QC",
            blank_label="study",
            sample_metadata_column="sampletype",
            na_rm=True,
        )
        self._compare_features(xcms_experiment_filtered, "blank_flag")

    def _compare_features(self, xcms_experiment, _filter):
        features_exp = pd.read_csv(
            self.get_data_path(
                f"filtered_features/xcms_experiment_feature_definitions_{_filter}.txt"
            ),
            sep="\t",
            index_col=0,
        )
        features_obs = pd.read_csv(
            os.path.join(
                str(xcms_experiment), "xcms_experiment_feature_definitions.txt"
            ),
            sep="\t",
            index_col=0,
        )
        pd.testing.assert_frame_equal(features_exp, features_obs)
