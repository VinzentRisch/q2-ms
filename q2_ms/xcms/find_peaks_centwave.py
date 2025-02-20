import copy

from q2_ms.types import XCMSExperimentDirFmt, mzMLDirFmt
from q2_ms.utils import run_r_script
from q2_ms.xcms.utils import change_data_paths


def find_peaks_centwave(
    spectra: mzMLDirFmt,
    xcms_experiment: XCMSExperimentDirFmt,
    ppm: float = 25,
    min_peak_width: float = 20,
    max_peak_width: float = 50,
    sn_thresh: float = 10,
    prefilter_k: float = 3,
    prefilter_i: float = 100,
    mz_center_fun: str = "wMean",
    integrate: int = 1,
    mz_diff: float = -0.001,
    fit_gauss: bool = False,
    noise: float = 0,
    first_baseline_check: bool = True,
    ms_level: int = 1,
    extend_length_msw: bool = False,
    verbose_columns: bool = False,
    verbose_beta_columns: bool = False,
    threads: int = 1,
) -> XCMSExperimentDirFmt:
    # Create parameters dict
    params = copy.copy(locals())

    # Init XCMSExperimentDirFmt
    xcms_experiment_peaks = XCMSExperimentDirFmt()

    # Change data paths in xcms experiment
    change_data_paths(str(xcms_experiment), str(spectra))

    # Add output path to params
    params["output_path"] = str(xcms_experiment_peaks)

    # Run R script
    run_r_script(params, "find_peaks_centwave", "XCMS")

    return xcms_experiment_peaks
