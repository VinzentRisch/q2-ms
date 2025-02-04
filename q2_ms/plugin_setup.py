# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from q2_types.sample_data import SampleData
from qiime2.core.type import Bool, Choices, Float, Int, Properties, Range, Str
from qiime2.plugin import Citations, Metadata, Plugin

from q2_ms import __version__
from q2_ms.types import mzML, mzMLDirFmt, mzMLFormat
from q2_ms.types._format import (
    MSBackendDataFormat,
    MSExperimentLinkMColsFormat,
    MSExperimentSampleDataFormat,
    MSExperimentSampleDataLinksSpectra,
    SpectraSlotsFormat,
    XCMSExperimentChromPeakDataFormat,
    XCMSExperimentChromPeaksFormat,
    XCMSExperimentDirFmt,
    XCMSExperimentFeatureDefinitionsFormat,
    XCMSExperimentFeaturePeakIndexFormat,
    XCMSExperimentJSONFormat,
)
from q2_ms.types._type import XCMSExperiment
from q2_ms.xcms.adjust_retention_time_obiwarp import adjust_retention_time_obiwarp
from q2_ms.xcms.filter_features import filter_features
from q2_ms.xcms.find_peaks_centwave import find_peaks_centwave
from q2_ms.xcms.group_peaks_density import group_peaks_density

citations = Citations.load("citations.bib", package="q2_ms")

plugin = Plugin(
    name="ms",
    version=__version__,
    website="https://github.com/bokulich-lab/q2-ms",
    package="q2_ms",
    description="A QIIME 2 plugin for MS data processing.",
    short_description="A QIIME 2 plugin for MS data processing.",
)

plugin.methods.register_function(
    function=find_peaks_centwave,
    inputs={"spectra": SampleData[mzML]},
    outputs=[("xcms_experiment", XCMSExperiment % Properties("Peaks"))],
    parameters={
        "sample_metadata": Metadata,
        "ppm": Float,
        "min_peakwidth": Float,
        "max_peakwidth": Float,
        "snthresh": Float,
        "prefilter_k": Float,
        "prefilter_i": Float,
        "mz_center_fun": Str
        % Choices(["wMean", "mean", "apex", "wMeanApex3", "meanApex3"]),
        "integrate": Int % Range(1, 3),
        "mzdiff": Float,
        "fitgauss": Bool,
        "noise": Float,
        "first_baseline_check": Bool,
        "ms_level": Int,
        "threads": Int,
    },
    input_descriptions={"spectra": "Spectra data as mzML files."},
    output_descriptions={
        "xcms_experiment": (
            "XCMSExperiment object with chromatographic peak information exported to "
            "plain text."
        )
    },
    parameter_descriptions={
        "sample_metadata": (
            "Metadata with the sample annotations. The index column should be called "
            "'sampleid' and should be identical to the filename. The second column "
            "should be called 'samplegroup'."
        ),
        "ppm": (
            "Defines the maximal tolerated m/z deviation in consecutive scans in parts "
            "per million (ppm) for the initial ROI definition."
        ),
        "min_peakwidth": (
            "Defines the minimal expected approximate peak width in chromatographic "
            "space in seconds."
        ),
        "max_peakwidth": (
            "Defines the maximal expected approximate peak width in chromatographic "
            "space in seconds."
        ),
        "snthresh": "Defines the signal to noise ratio cutoff.",
        "prefilter_k": (
            "Specifies the prefilter step for the first analysis step (ROI detection). "
            "Mass traces are only retained if they contain at least k peaks."
        ),
        "prefilter_i": (
            "Specifies the prefilter step for the first analysis step (ROI detection). "
            "Mass traces are only retained if they contain peaks with intensity >= i."
        ),
        "mz_center_fun": (
            "Name of the function to calculate the m/z center of the chromatographic "
            'peak. Allowed are: "wMean": intensity weighted mean of the peaks '
            'm/z values, "mean": mean of the peaks m/z values, "apex": use the m/z '
            'value at the peak apex, "wMeanApex3": intensity weighted mean of the '
            "m/z value at the peak apex and the m/z values left and right of it and "
            '"meanApex3": mean of the m/z value of the peak apex and the m/z values '
            "left and right of it."
        ),
        "integrate": (
            "Integration method. For integrate = 1 peak limits are found through "
            "descent on the mexican hat filtered data, for integrate = 2 the descent "
            "is done on the real data. The latter method is more accurate but prone "
            "to noise, while the former is more robust, but less exact."
        ),
        "mzdiff": (
            "Represents the minimum difference in m/z dimension required for peaks with"
            " overlapping retention times; can be negative to allow overlap. During "
            "peak post-processing, peaks defined to be overlapping are reduced to the "
            "one peak with the largest signal."
        ),
        "fitgauss": (
            "Whether or not a Gaussian should be fitted to each peak. This affects "
            "mostly the retention time position of the peak."
        ),
        "noise": (
            "Allowing to set a minimum intensity required for centroids to be "
            "considered in the first analysis step (centroids with intensity < noise "
            "are omitted from ROI detection)."
        ),
        "first_baseline_check": (
            "If TRUE continuous data within regions of interest is checked to be above "
            "the first baseline."
        ),
        "ms_level": (
            "Defines the MS level on which the peak detection should be performed."
        ),
        "threads": "Number of threads to be used.",
    },
    name="Find chromatographic peaks with centWave",
    description=(
        "This function uses the XCMS and the centWave algorithm to perform peak "
        "density and wavelet based chromatographic peak detection for high resolution "
        "LC/MS data."
    ),
    citations=[
        citations["kosters2018pymzml"],
        citations["tautenhahn2008highly"],
        citations["smith2006xcms"],
        citations["msexperiment2024"],
    ],
)

plugin.methods.register_function(
    function=adjust_retention_time_obiwarp,
    inputs={
        "spectra": SampleData[mzML],
        "chromatographic_peaks": XCMSExperiment % Properties("Peaks"),
    },
    outputs=[("retention_time_adjustment", XCMSExperiment % Properties("RT_adjusted"))],
    parameters={
        "bin_size": Float,
        "center_sample": Int,
        "response": Float,
        "dist_fun": Str % Choices(["cor_opt", "cor", "cov", "prd", "euc"]),
        "gap_init": Float,
        "gap_extend": Float,
        "factor_diag": Float,
        "factor_gap": Float,
        "local_alignment": Bool,
        "init_penalty": Float,
        "subset": Int,
        "subset_adjust": Str % Choices(["previous", "average"]),
        "rtime_difference_threshold": Float,
        "chunk_size": Int,
        "threads": Int,
    },
    input_descriptions={
        "spectra": "Spectra data as mzML files.",
        "chromatographic_peaks": "XCMSExperiment object with chromatographic peak "
        "information.",
    },
    output_descriptions={
        "retention_time_adjustment": (
            "XCMSExperiment object with retention time adjustments exported to plain "
            "text."
        )
    },
    parameter_descriptions={
        "bin_size": (
            "Defines the bin size (in m/z dimension) to be used for the profile matrix "
            "generation. See step parameter in profile-matrix documentation for more "
            "details."
        ),
        "center_sample": (
            "Defines the index of the center sample in the experiment. Defaults to "
            "floor(median(1:length(fileNames(object)))). Note that if subset is used, "
            "the index passed with center_sample is within these subset samples."
        ),
        "response": (
            "Defines the responsiveness of warping, with response = 0 giving linear "
            "warping on start and end points and response = 100 warping using all "
            "bijective anchors."
        ),
        "dist_fun": (
            "Defines the distance function to be used. Allowed values are: 'cor' "
            "(Pearson correlation), 'cor_opt' (optimized diagonal band correlation), "
            "'cov' (covariance), 'prd' (product), and 'euc' (Euclidean distance). The "
            "default value is 'cor_opt'."
        ),
        "gap_init": (
            "Defines the penalty for gap opening. Default values depend on the "
            "distance function: for 'cor' and 'cor_opt' it is 0.3, for 'cov' and 'prd' "
            "0.0, and for 'euc' 0.9."
        ),
        "gap_extend": (
            "Defines the penalty for gap enlargement. Default values depend on the "
            "distance function: for 'cor' and 'cor_opt' it is 2.4, for 'cov' 11.7, for "
            "'euc' 1.8, and for 'prd' 7.8."
        ),
        "factor_diag": (
            "Defines the local weight applied to diagonal moves in the alignment."
        ),
        "factor_gap": ("Defines the local weight for gap moves in the alignment."),
        "local_alignment": (
            "Specifies whether a local alignment should be performed instead of the "
            "default global alignment."
        ),
        "init_penalty": (
            "Defines the penalty for initiating an alignment (for local alignment "
            "only)."
        ),
        "subset": (
            "Defines the indices of samples within the experiment on which the "
            "alignment models should be estimated. Samples not part of the subset are "
            "adjusted based on the closest subset sample."
        ),
        "subset_adjust": (
            "Specifies the method with which non-subset samples should be adjusted. "
            "Supported options are 'previous' and 'average' (default)."
        ),
        "rtime_difference_threshold": (
            "Defines the retention time difference threshold for alignment."
        ),
        "chunk_size": ("Specifies the size of chunks used during processing."),
    },
    name="Retention time adjustment with Obiwarp",
    description=(
        "This function uses XCMS and the Obiwarp algorithm to perform retention time "
        "adjustment for high resolution LC/MS data."
    ),
    citations=[
        citations["kosters2018pymzml"],
        citations["lange2008critical"],
        citations["smith2006xcms"],
        citations["msexperiment2024"],
    ],
)

plugin.methods.register_function(
    function=group_peaks_density,
    inputs={
        "xcms_experiment": XCMSExperiment % Properties("RT_adjusted"),
    },
    outputs=[("xcms_experiment_grouped", XCMSExperiment % Properties("Grouped"))],
    parameters={
        "bw": Float,
        "min_fraction": Float,
        "min_samples": Float,
        "bin_size": Float,
        "max_features": Float,
        "ms_level": Int,
        "threads": Int,
    },
    input_descriptions={
        "xcms_experiment": "XCMSExperiment object with chromatographic peak "
        "information and adjusted retention time.",
    },
    output_descriptions={
        "xcms_experiment_grouped": (
            "XCMSExperiment object with grouped chromatographic peak "
            "information and adjusted retention time."
        )
    },
    parameter_descriptions={
        "bw": (
            "Defining the bandwidth (standard deviation ot the smoothing kernel) to be "
            "used."
        ),
        "min_fraction": (
            "Defining the minimum fraction of samples in at least one sample group in "
            "which the peaks have to be present to be considered as a peak group "
            "(feature)."
        ),
        "min_samples": (
            "With the minimum number of samples in at least one sample group in which "
            "the peaks have to be detected to be considered a peak group (feature)."
        ),
        "bin_size": ("Defining the size of the overlapping slices in mz dimension."),
        "max_features": (
            "The maximum number of peak groups to be identified in a single mz slice."
        ),
        "ms_level": (
            "defining the MS level on which the correspondence should be performed. "
            "It is required that chromatographic peaks of the respective MS level are "
            "present."
        ),
        "threads": (
            "Defines the local weight applied to diagonal moves in the alignment."
        ),
    },
    name="Correspondence based on density",
    description=(
        "This method performs performs correspondence (chromatographic peak grouping) "
        "based on the density (distribution) of identified peaks along the retention "
        "time axis within slices of overlapping mz ranges."
    ),
    citations=[
        citations["kosters2018pymzml"],
        citations["smith2006xcms"],
        citations["msexperiment2024"],
    ],
)

plugin.methods.register_function(
    function=filter_features,
    inputs={
        "xcms_experiment": XCMSExperiment % Properties("Grouped"),
    },
    outputs=[("xcms_experiment_filtered", XCMSExperiment % Properties("Grouped"))],
    parameters={
        "filter": Str % Choices(["rsd", "d-ratio", "percent-missing", "blank-flag"]),
        "threshold": Float,
        "f": Str,
        "qc_index": Str,
        "study_index": Str,
        "blank_index": Str,
        "na_rm": Bool,
        "mad": Bool,
    },
    input_descriptions={
        "xcms_experiment": "XCMSExperiment object with detected features."
    },
    output_descriptions={
        "xcms_experiment_filtered": ("XCMSExperiment object with filtered features.")
    },
    parameter_descriptions={
        "filter": (
            "Specifies the filtering method to be applied. Options include "
            "'rsd' for filtering based on the relative standard deviation in "
            "QC samples, 'd-ratio' for filtering based on the dispersion ratio "
            "between QC and study samples, 'percent-missing' for filtering based "
            "on the percentage of missing values in sample groups, and "
            "'blank-flag' for identifying features that may result from "
            "contamination in blank samples."
        ),
        "threshold": (
            "Defines the threshold value for the selected filter. Default values "
            "depend on the chosen filter: \n"
            "- 'rsd': 0.3 (maximum coefficient of variation in QC samples)\n"
            "- 'd-ratio': 0.5 (maximum dispersion ratio between QC and study)\n"
            "- 'percent-missing': 30 (maximum % of missing values per group)\n"
            "- 'blank-flag': 2 (multiple of mean abundance in blanks for filtering)"
        ),
        "f": (
            "A vector indicating the sample group for each sample. This is used "
            "in 'percent-missing' to determine the percentage of missing values "
            "within each group."
        ),
        "qc_index": (
            "A logical vector indicating which samples are Quality Control (QC) "
            "samples. This is used in 'rsd' and 'd-ratio' to calculate the "
            "relative standard deviation and dispersion ratio, respectively."
        ),
        "study_index": (
            "A logical vector indicating which samples are study samples. This is "
            "used in 'd-ratio' to calculate the dispersion ratio between QC and "
            "study samples."
        ),
        "blank_index": (
            "A logical vector indicating which samples are blank samples. This is "
            "used in 'blank-flag' to identify features that may result from "
            "contamination in the solvent of the samples."
        ),
        "na_rm": (
            "A logical value indicating whether to remove features with missing "
            "values. Default is TRUE for 'rsd', 'd-ratio', and 'blank-flag'."
        ),
        "mad": (
            "A logical value indicating whether to use the median absolute "
            "deviation (MAD) for robust estimation of variability. Default is "
            "FALSE for 'rsd' and 'd-ratio'."
        ),
    },
    name="Feature filtering based on sample characteristics",
    description=(
        "This method filters detected features based on their characteristics across "
        "different sample groups. It applies user-defined thresholds to exclude "
        "features that exhibit excessive variability in QC samples, imbalanced "
        "presence across study groups, or potential contamination from blank samples. "
        "This action uses the filterFeatures() function of the XCMS package."
    ),
    citations=[
        citations["kosters2018pymzml"],
        citations["smith2006xcms"],
        citations["msexperiment2024"],
    ],
)

# Registrations
plugin.register_semantic_types(
    mzML,
    XCMSExperiment,
)

plugin.register_semantic_type_to_format(SampleData[mzML], artifact_format=mzMLDirFmt)
plugin.register_semantic_type_to_format(
    XCMSExperiment, artifact_format=XCMSExperimentDirFmt
)

plugin.register_formats(
    mzMLFormat,
    mzMLDirFmt,
    MSBackendDataFormat,
    MSExperimentLinkMColsFormat,
    MSExperimentSampleDataFormat,
    MSExperimentSampleDataLinksSpectra,
    SpectraSlotsFormat,
    XCMSExperimentChromPeakDataFormat,
    XCMSExperimentChromPeaksFormat,
    XCMSExperimentDirFmt,
    XCMSExperimentFeatureDefinitionsFormat,
    XCMSExperimentFeaturePeakIndexFormat,
    XCMSExperimentJSONFormat,
)
