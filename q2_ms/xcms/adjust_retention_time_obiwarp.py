import copy

from q2_ms.types import XCMSExperimentDirFmt, mzMLDirFmt
from q2_ms.utils import run_r_script
from q2_ms.xcms.utils import change_data_paths


def adjust_retention_time_obiwarp(
    spectra: mzMLDirFmt,
    xcms_experiment: XCMSExperimentDirFmt,
    bin_size: float = 25,
    center_sample: str = None,
    response: float = 1,
    dist_fun: str = "cor_opt",
    gap_init: float = None,
    gap_extend: float = None,
    factor_diag: float = 2,
    factor_gap: float = 1,
    local_alignment: bool = False,
    init_penalty: float = None,
    sample_metadata_column: str = None,
    subset_label: str = None,
    subset_adjust: str = None,
    rtime_difference_threshold: float = 5,
    chunk_size: int = 1,
    threads: int = 1,
) -> XCMSExperimentDirFmt:
    _validate_parameters(
        sample_metadata_column,
        subset_label,
        subset_adjust,
        local_alignment,
        init_penalty,
    )
    # Create parameters dict
    params = copy.copy(locals())

    # Innit XCMSExperimentDirFmt
    xcms_experiment_aligned = XCMSExperimentDirFmt()

    # Change data paths in xcms experiment
    change_data_paths(str(xcms_experiment), str(spectra))

    # Add output path to params
    params["output_path"] = str(xcms_experiment_aligned)

    # Run R script
    run_r_script(params, "adjust_retention_time_obiwarp", "XCMS")

    return xcms_experiment_aligned


def _validate_parameters(
    sample_metadata_column, subset_label, subset_adjust, local_alignment, init_penalty
):
    if bool(sample_metadata_column) != bool(subset_label) or bool(
        sample_metadata_column
    ) != bool(subset_adjust):
        raise ValueError(
            'The parameters "--p-sample-metadata-column",  "--p-subset-label" and '
            '"--p-subset-adjust" have to be used in combination with each other.'
        )

    if not local_alignment and init_penalty:
        raise ValueError(
            'The parameter "--p-init-penalty" can only be used if '
            '"--p-local-alignment" is set to True.'
        )
