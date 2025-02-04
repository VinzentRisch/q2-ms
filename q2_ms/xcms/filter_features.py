import copy

from q2_ms.types import XCMSExperimentDirFmt
from q2_ms.utils import run_r_script
from q2_ms.xcms.utils import create_fake_mzml_files


def filter_features(
    xcms_experiment: XCMSExperimentDirFmt,
    filter: str = None,
    threshold: float = None,
    f: str = None,
    qc_index: str = None,
    study_index: str = None,
    blank_index: str = None,
    na_rm: bool = True,
    mad: bool = False,
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
    run_r_script(params, "filter_features", "XCMS")

    return xcms_experiment
