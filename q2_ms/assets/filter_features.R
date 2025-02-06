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
  make_option(opt_str = "--f", type = "character"),
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

if (opt$xcms_experiment == "rsd") {
    filter <- RsdFilter(
      qcIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$qc_label,
      na.rm = opt$na_rm,
      mad = opt$mad
    )
} else if (opt$xcms_experiment == "d_ratio") {
    filter <- DratioFilter(
      qcIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$qc_label,
      studyIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$study_label,
      na.rm = opt$na_rm,
      mad = opt$mad
    )
} else if (opt$xcms_experiment == "percent_missing") {
    filter <- PercentMissingFilter(
      f = eval(parse(text = opt$f)),
    )
} else {
    filter <- BlankFlag(
      blankIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$blank_label,
      qcIndex = sampleData(XCMSExperiment)[[opt$sample_metadata_column]] == opt$qc_label,
      na.rm = opt$na_rm,
    )
}
print(opt)
print(filter)
if (!is.null(opt$threshold)) filter@threshold <- opt$threshold
# Filter features
XCMSExperiment <- filterFeatures(object = XCMSExperiment, filter = filter)

# Export the XCMSExperiment object to the directory format
saveMsObject(XCMSExperiment, param = PlainTextParam(path = opt$output_path))
