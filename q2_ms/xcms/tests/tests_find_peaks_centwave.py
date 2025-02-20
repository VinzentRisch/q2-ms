import os
from shutil import copytree

import pandas as pd
from qiime2.plugin.testing import TestPluginBase

from q2_ms.types import XCMSExperimentDirFmt, mzMLDirFmt
from q2_ms.xcms.find_peaks_centwave import find_peaks_centwave


class TestFindPeaksCentWave(TestPluginBase):
    package = "q2_ms.xcms.tests"

    def test_find_peaks_centwave(self):
        xcms_experiment = XCMSExperimentDirFmt()
        copytree(
            self.get_data_path("xcms_experiment_read_in"),
            str(xcms_experiment),
            dirs_exist_ok=True,
        )
        spectra = mzMLDirFmt()
        copytree(self.get_data_path("faahKO"), str(spectra), dirs_exist_ok=True)
        xcms_experiment_peaks = find_peaks_centwave(
            spectra=spectra,
            xcms_experiment=xcms_experiment,
            min_peak_width=20,
            max_peak_width=80,
            noise=4500,
            prefilter_i=5000,
            prefilter_k=6,
            mz_center_fun="mean",
            integrate=2,
            mz_diff=-0.002,
            fit_gauss=True,
            ppm=28,
            sn_thresh=12,
            first_baseline_check=False,
            extend_length_msw=True,
            verbose_columns=True,
            verbose_beta_columns=True,
        )
        chrom_peaks_exp = pd.read_csv(
            self.get_data_path("chrom_peaks_R/xcms_experiment_chrom_peaks.txt"),
            sep="\t",
            index_col=0,
        )
        chrom_peaks_obs = pd.read_csv(
            os.path.join(str(xcms_experiment_peaks), "xcms_experiment_chrom_peaks.txt"),
            sep="\t",
            index_col=0,
        )
        pd.testing.assert_frame_equal(chrom_peaks_exp, chrom_peaks_obs)
