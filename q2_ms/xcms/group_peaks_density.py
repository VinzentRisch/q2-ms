import copy

from q2_ms.types import XCMSExperimentDirFmt
from q2_ms.utils import run_r_script
from q2_ms.xcms.utils import create_fake_mzml_files


def group_peaks_density(
    xcms_experiment: XCMSExperimentDirFmt,
    bw: float = 30,
    min_fraction: float = 0.5,
    min_samples: float = 1,
    bin_size: float = 0.25,
    max_features: float = 50,
    ppm: float = 0,
    sample_metadata_column: str = None,
    ms_level: int = 1,
    add: bool = False,
    threads: int = 1,
) -> XCMSExperimentDirFmt:
    # Create fake mzML files to make the xcms experiment object import possible
    create_fake_mzml_files(str(xcms_experiment))

    # Create parameters dict
    params = copy.copy(locals())

    # Innit XCMSExperimentDirFmt
    xcms_experiment = XCMSExperimentDirFmt()

    # Add output path to params
    params["output_path"] = str(xcms_experiment)

    # Run R script
    run_r_script(params, "group_peaks_density", "XCMS")

    return xcms_experiment
