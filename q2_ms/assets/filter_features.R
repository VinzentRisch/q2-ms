#!/usr/local/bin/Rscript --vanilla

library(xcms)
library(MsExperiment)
library(MsIO)
library(Spectra)
library(optparse)

# Define command-line options
option_list <- list(
  make_option(opt_str = "--xcms_experiment", type = "character"),
  make_option(opt_str = "--filter", type = "character"),
  make_option(opt_str = "--threshold", type = "numeric"),
  make_option(opt_str = "--exclude", type = "logical"),
  make_option(opt_str = "--qc_label", type = "character"),
  make_option(opt_str = "--study_label", type = "character"),
  make_option(opt_str = "--blank_label", type = "character"),
  make_option(opt_str = "--sample_metadata_column", type = "character"),
  make_option(opt_str = "--na_rm", type = "logical"),
  make_option(opt_str = "--mad", type = "logical"),
  make_option(opt_str = "--output_path", type = "character")
)
# Parse arguments
optParser <- OptionParser(option_list = option_list)
opt <- parse_args(optParser)
XCMSExperiment <- readMsObject(XcmsExperiment(), PlainTextParam(opt$xcms_experiment))

# Set parameters
if (opt$filter == "rsd") {
    filter <- RsdFilter(
      qcIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$qc_label,
    )
    if (!is.null(opt$na_rm)) filter@na.rm <- opt$na_rm
    if (!is.null(opt$mad)) filter@mad <- opt$mad

} else if (opt$filter == "d_ratio") {
    filter <- DratioFilter(
      qcIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$qc_label,
      studyIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$study_label,
    )
    if (!is.null(opt$na_rm)) filter@na.rm <- opt$na_rm
    if (!is.null(opt$mad)) filter@mad <- opt$mad

} else if (opt$filter == "percent_missing") {
    f <- sampleData(XCMSExperiment)[[opt$sample_metadata_column]]
    if (isTRUE(opt$exclude)){
        f[f == opt$qc_label] <- NA
    }
    else if (isFALSE(opt$exclude)){
        f[f != opt$qc_label] <- NA
    }
    filter <- PercentMissingFilter(f = f)

} else {
    filter <- BlankFlag(
      blankIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$blank_label,
      qcIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$qc_label,
    )
    if (!is.null(opt$na_rm)) filter@na.rm <- opt$na_rm
}

if (!is.null(opt$threshold)) filter@threshold <- opt$threshold

# Filter features
XCMSExperiment <- filterFeatures(object = XCMSExperiment, filter = filter)

# Export the XCMSExperiment object to the directory format
saveMsObject(XCMSExperiment, param = PlainTextParam(path = opt$output_path))
