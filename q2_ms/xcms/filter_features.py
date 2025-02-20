import copy

from q2_ms.types import XCMSExperimentDirFmt
from q2_ms.utils import run_r_script
from q2_ms.xcms.utils import create_fake_mzml_files


def filter_features(
    xcms_experiment: XCMSExperimentDirFmt,
    filter: str = None,
    threshold: float = None,
    exclude: bool = None,
    qc_label: str = "qc",
    study_label: str = "study",
    blank_label: str = "blank",
    sample_metadata_column: str = None,
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


def validate_parameters(
    filter: str = None,
    threshold: float = None,
    f: str = None,
    qc_label: str = None,
    study_label: str = None,
    blank_label: str = None,
    sample_metadata_column: str = None,
    na_rm: bool = True,
    mad: bool = False,
):
    # Define valid parameter combinations for each filter
    valid_combinations = {
        "rsd": {"threshold", "qc_label", "na_rm", "mad", "sample_metadata_column"},
        "d-ratio": {
            "threshold",
            "qc_label",
            "study_label",
            "na_rm",
            "mad",
            "sample_metadata_column",
        },
        "percent-missing": {
            "threshold",
            "exclude",
            "qc_label",
            "sample_metadata_column",
        },
        "blank-flag": {
            "threshold",
            "qc_label",
            "blank_label",
            "na_rm",
            "sample_metadata_column",
        },
    }

    # Store the provided parameters using locals()
    provided_params = {k: v for k, v in locals().items() if k != "filter"}

    # Check if any provided parameter is not allowed for the selected filter
    for param, value in provided_params.items():
        if value is not None and param not in valid_combinations[filter]:
            raise ValueError(
                f"The parameter '{param}' cannot be used in combination with the "
                f"filter '{filter}'."
            )
