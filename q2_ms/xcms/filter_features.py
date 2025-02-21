import copy

from q2_ms.types import XCMSExperimentDirFmt
from q2_ms.utils import run_r_script
from q2_ms.xcms.utils import create_fake_mzml_files


def filter_features(
    xcms_experiment: XCMSExperimentDirFmt,
    filter: str = None,
    threshold: float = None,
    exclude: bool = None,
    qc_label: str = None,
    study_label: str = None,
    blank_label: str = None,
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
    exclude: str = None,
    qc_label: str = None,
    study_label: str = None,
    blank_label: str = None,
    sample_metadata_column: str = None,
    na_rm: bool = None,
    mad: bool = None,
):
    # Store the provided parameters using locals()
    parameters = {k: v for k, v in locals().items() if k != "filter"}

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

    # Check if any provided parameter is not allowed for the selected filter
    for param, value in parameters.items():
        if value is not None and param not in valid_combinations[filter]:
            raise ValueError(
                f"The parameter '{param}' cannot be used in combination with the "
                f"filter '{filter}'."
            )
    if filter == "percent-missing":
        parameters_percent_missing = [exclude, qc_label, sample_metadata_column]

        if not (
            all(param is None for param in parameters_percent_missing)
            or all(param is not None for param in parameters_percent_missing)
        ):
            raise ValueError(
                "If the percent-missing filter is used, the parameters 'exclude', "
                "'qc-label' and 'sample-metadata-column' have to be used in "
                "combination or not at all."
            )
