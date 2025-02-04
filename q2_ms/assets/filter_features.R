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
  make_option(opt_str = "--qc_index", type = "character"),
  make_option(opt_str = "--study_index", type = "character"),
  make_option(opt_str = "--blank_index", type = "character"),
  make_option(opt_str = "--na_rm", type = "logical"),
  make_option(opt_str = "--mad", type = "logical"),
  make_option(opt_str = "--output_path", type = "character"),
)

# Parse arguments
optParser <- OptionParser(option_list = option_list)
opt <- parse_args(optParser)

XCMSExperiment <- readMsObject(XcmsExperiment(), PlainTextParam(opt$xcms_experiment))

if (opt$xcms_experiment == "rsd") {
    filter <- RsdFilter(
      threshold = opt$threshold,
      qcIndex = opt$qc_index,
      na.rm = opt$na_rm,
      mad = FALSE
    )
} else if (opt$xcms_experiment == "d_ratio") {
    filter <- DratioFilter(
      threshold = opt$threshold,
      qcIndex = opt$qc_index,
      studyIndex = opt$study_index,
      na.rm = opt$na_rm,
      mad = FALSE
    )
} else if (opt$xcms_experiment == "percent_missing") {
    filter <- PercentMissingFilter(
      threshold = opt$threshold,
      f = eval(parse(text = opt$f)),
    )
} else {
    filter <- BlankFlag(
      threshold = opt$threshold,
      blankIndex = opt$blank_index,
      qcIndex = opt$qc_index,
      na.rm = opt$na_rm,
    )
}

# Set parameters
DensityParams <- PeakDensityParam(
  sampleGroups = sampleData(XCMSExperiment)$samplegroup,
  bw = opt$bw,
  minFraction = opt$min_fraction,
  minSamples = opt$min_samples,
  binSize = opt$bin_size,
  maxFeatures = opt$max_features
)


# Filter features
XCMSExperiment <- filterFeatures(object = XCMSExperiment, filter = filter)

# Export the XCMSExperiment object to the directory format
saveMsObject(XCMSExperiment, param = PlainTextParam(path = opt$output_path))
