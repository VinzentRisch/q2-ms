# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from q2_types.sample_data import SampleData
from qiime2.core.type import Bool, Choices, Float, Int, Properties, Range, Str, TypeMap
from qiime2.plugin import Citations, Plugin

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

I_find_peaks, O_find_peaks = TypeMap(
    {
        XCMSExperiment: XCMSExperiment % Properties("peaks"),
        XCMSExperiment
        % Properties("rt-adjusted"): XCMSExperiment
        % Properties("peaks", "rt-adjusted"),
    }
)

plugin.methods.register_function(
    function=find_peaks_centwave,
    inputs={
        "spectra": SampleData[mzML],
        "xcms_experiment": I_find_peaks,
    },
    outputs=[("xcms_experiment_peaks", O_find_peaks)],
    parameters={
        "ppm": Float % Range(0, None),
        "min_peak_width": Float % Range(0, None),
        "max_peak_width": Float % Range(0, None),
        "sn_thresh": Float % Range(0, None),
        "prefilter_k": Float,
        "prefilter_i": Float,
        "mz_center_fun": Str
        % Choices(["wMean", "mean", "apex", "wMeanApex3", "meanApex3"]),
        "integrate": Int % Range(1, 3),
        "mz_diff": Float,
        "fit_gauss": Bool,
        "noise": Float,
        "first_baseline_check": Bool,
        "ms_level": Int % Range(1, 3),
        "threads": Int % Range(1, None),
        "extend_length_msw": Bool,
        "verbose_columns": Bool,
        "verbose_beta_columns": Bool,
    },
    input_descriptions={
        "spectra": "Spectra data as mzML files.",
        "xcms_experiment": "XCMSExperiment object exported to plain text.",
    },
    output_descriptions={
        "xcms_experiment_peaks": (
            "XCMSExperiment object with chromatographic peak information exported to "
            "plain text."
        )
    },
    parameter_descriptions={
        "ppm": (
            "Defines the maximal tolerated m/z deviation in consecutive scans in parts "
            "per million (ppm) for the initial ROI definition."
        ),
        "min_peak_width": (
            "Defines the minimal expected approximate peak width in chromatographic "
            "space in seconds."
        ),
        "max_peak_width": (
            "Defines the maximal expected approximate peak width in chromatographic "
            "space in seconds."
        ),
        "sn_thresh": "Defines the signal to noise ratio cutoff.",
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
        "mz_diff": (
            "Represents the minimum difference in m/z dimension required for peaks with"
            " overlapping retention times; can be negative to allow overlap. During "
            "peak post-processing, peaks defined to be overlapping are reduced to the "
            "one peak with the largest signal."
        ),
        "fit_gauss": (
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
        "extend_length_msw": (
            "Option to force centWave to use all scales when running centWave rather "
            "than truncating with the EIC length. Uses the 'open' method to extend the "
            "EIC to a integer base-2 length prior to being passed to 'convolve' rather "
            "than the default 'reflect' method. See "
            "https://github.com/sneumann/xcms/issues/445 for more information."
        ),
        "verbose_columns": (
            "Option to add additional peak meta data columns to the peaks data."
        ),
        "verbose_beta_columns": (
            "Option to calculate two additional metrics of peak quality via comparison "
            "to an idealized bell curve. Adds 'beta_cor' and 'beta_snr' to the "
            "'chromPeaks' output, corresponding to a Pearson correlation coefficient "
            "to a bell curve with several degrees of skew as well as an estimate of "
            "signal-to-noise using the residuals from the best-fitting bell curve. "
            "See https://github.com/sneumann/xcms/pull/685 and "
            "https://doi.org/10.1186/s12859-023-05533-4 for more information."
        ),
    },
    name="Find chromatographic peaks with centWave",
    description=(
        "This function uses XCMS and the centWave algorithm to perform peak "
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

I_adjust_rt, O_adjust_rt = TypeMap(
    {
        XCMSExperiment: XCMSExperiment % Properties("rt-adjusted"),
        XCMSExperiment
        % Properties("peaks"): XCMSExperiment
        % Properties("peaks", "rt-adjusted"),
        XCMSExperiment
        % Properties("features"): XCMSExperiment
        % Properties("features", "rt-adjusted"),
        XCMSExperiment
        % Properties("filled"): XCMSExperiment
        % Properties("filled", "rt-adjusted"),
    }
)

plugin.methods.register_function(
    function=adjust_retention_time_obiwarp,
    inputs={
        "spectra": SampleData[mzML],
        "xcms_experiment": I_adjust_rt,
    },
    outputs=[("xcms_experiment_rt_adjusted", O_adjust_rt)],
    parameters={
        "bin_size": Float % Range(0, None, inclusive_start=False),
        "center_sample": Str,
        "response": Float % Range(0, 100, inclusive_end=True),
        "dist_fun": Str % Choices(["cor_opt", "cor", "cov", "prd", "euc"]),
        "gap_init": Float,
        "gap_extend": Float,
        "factor_diag": Float % Range(0, None),
        "factor_gap": Float % Range(0, None),
        "local_alignment": Bool,
        "init_penalty": Float % Range(0, None),
        "sample_metadata_column": Str,
        "subset_label": Str,
        "subset_adjust": Str % Choices(["previous", "average"]),
        "rtime_difference_threshold": Float,
        "chunk_size": Int % Range(0, None, inclusive_start=False),
        "threads": Int % Range(0, None, inclusive_start=False),
    },
    input_descriptions={
        "spectra": "Spectra data as mzML files.",
        "xcms_experiment": "XCMSExperiment object.",
    },
    output_descriptions={
        "xcms_experiment_rt_adjusted": (
            "XCMSExperiment object with retention time adjustments."
        )
    },
    parameter_descriptions={
        "bin_size": (
            "Defines the bin size (in m/z dimension) to be used for the profile matrix "
            "generation."
        ),
        "center_sample": (
            "Defines the name of the center sample in the experiment. Defaults to "
            "the median index in the sample data. Note that if subset is used, the "
            "index passed with center_sample is within these subset samples."
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
        "factor_gap": "Defines the local weight for gap moves in the alignment.",
        "local_alignment": (
            "Specifies whether a local alignment should be performed instead of the "
            "default global alignment."
        ),
        "init_penalty": (
            "Defines the penalty for initiating an alignment (for local alignment "
            "only)."
        ),
        "sample_metadata_column": (
            "The sample metadata column that specifies the sample subset within the "
            "experiment on which the alignment models should be estimated. Samples "
            "not part of the subset are adjusted based on the closest subset sample. "
            "This parameter is used in combination with 'subset-label'."
        ),
        "subset_label": (
            "Specifies the label that is used to identify the subset samples in the "
            "sample metadata column."
        ),
        "subset_adjust": (
            "Specifies the method with which non-subset samples should be adjusted. "
            "Supported options are 'previous' and 'average'. With 'previous', each "
            "non-subset sample is adjusted based on the closest previous subset sample "
            "which results in most cases with adjusted retention times of the "
            "non-subset sample being identical to the subset sample on which the "
            "adjustment bases. The second, default, option is 'average' in which case "
            "each non subset sample is adjusted based on the average retention time "
            "adjustment from the previous and following subset sample. For the "
            "average, a weighted mean is used with weights being the inverse of the "
            "distance of the non-subset sample to the subset samples used for "
            "alignment."
        ),
        "rtime_difference_threshold": (
            "Defining the threshold to identify a gap in the sequence of retention "
            "times of (MS1) spectra of a sample/file. A gap is defined if the "
            "difference in retention times between consecutive spectra is > "
            "rtimeDifferenceThreshold of the median observed difference or retenion "
            "times of that data sample/file. Spectra with an retention time after such "
            "a gap will not be adjusted. The default for this parameter is "
            "rtimeDifferenceThreshold = 5. For Waters data with lockmass scans or "
            "LC-MS/MS data this might however be a too low threshold and it should "
            "be increased. See also https://github.com/sneumann/xcms/issues/739."
        ),
        "chunk_size": (
            "Defining the number of files (samples) that should be loaded into memory "
            "and processed at the same time. Alignment is then performed in parallel "
            "(per sample) on this subset of loaded data. This setting thus allows to "
            "balance between memory demand and speed (due to parallel processing). "
            "Because parallel processing can only performed on the subset of data "
            "currently loaded into memory in each iteration, the value for chunkSize "
            "should match the defined parallel setting setup. Using a parallel "
            "processing setup using 4 CPUs (separate processes) but using chunkSize = "
            "1 will not perform any parallel processing, as only the data from one "
            "sample is loaded in memory at a time. On the other hand, setting chunk "
            "size to the total number of samples in an experiment will load the full "
            "MS data into memory and will thus in most settings cause an out-of-memory "
            "error."
        ),
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
        "ppm": Float,
        "sample_metadata_column": Str,
        "ms_level": Int,
        "add": Bool,
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
        "bin_size": "Defining the size of the overlapping slices in mz dimension.",
        "max_features": (
            "The maximum number of peak groups to be identified in a single mz slice."
        ),
        "sample_metadata_column": (
            "The name of the sample metadata column that defines the sample groups. "
            "Per default all samples are added to the same group."
        ),
        "ppm": (
            "To define m/z-dependent, increasing m/z bin sizes. If ‘ppm = 0’ (the "
            "default) m/z bins are defined by the sequence of values from the smallest "
            "to the larges m/z value with a constant bin size of ‘bin-size’. For ‘ppm’ "
            "> 0 the size of each bin is increased in addition by the ‘ppm’ of the "
            "(upper) m/z boundary of the bin. The maximal bin size (used for the "
            "largest m/z values) would then be ‘bin-size’ plus ‘ppm’ parts-per-million "
            "of the largest m/z value of all peaks in the data set."
        ),
        "ms_level": (
            "defining the MS level on which the correspondence should be performed. "
            "It is required that chromatographic peaks of the respective MS level are "
            "present."
        ),
        "add": (
            "Allowing to perform an additional round of correspondence (e.g. on a "
            "different MS level) and add features to the already present feature "
            "definitions. Per default any additional grouping will remove previous "
            "results."
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
