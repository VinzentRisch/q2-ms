#!/usr/local/bin/Rscript --vanilla

library(xcms)
library(MsExperiment)
library(MsIO)
library(Spectra)
library(optparse)

# Define command-line options
option_list <- list(
  make_option(opt_str = "--xcms_experiment", type = "character"),
  make_option(opt_str = "--bw", type = "numeric"),
  make_option(opt_str = "--min_fraction", type = "numeric"),
  make_option(opt_str = "--min_samples", type = "numeric"),
  make_option(opt_str = "--bin_size", type = "numeric"),
  make_option(opt_str = "--max_features", type = "numeric"),
  make_option(opt_str = "--ppm", type = "numeric"),
  make_option(opt_str = "--sample_metadata_column", type = "character"),
  make_option(opt_str = "--add", type = "logical"),
  make_option(opt_str = "--output_path", type = "character"),
  make_option(opt_str = "--ms_level", type = "integer")
)

# Parse arguments
optParser <- OptionParser(option_list = option_list)
opt <- parse_args(optParser)

XCMSExperiment <- readMsObject(XcmsExperiment(), PlainTextParam(opt$xcms_experiment))

# Set sampleGroups parameter
if (!is.null(opt$sampleGroups)) {
  sampleGroups <- rep(1, length(fileNames(XCMSExperiment)))
} else {
  sampleGroups <- sampleData(XCMSExperiment)[[opt$sample_metadata_column]]
}

# Set parameters
DensityParams <- PeakDensityParam(
  sampleGroups = sampleGroups,
  bw = opt$bw,
  minFraction = opt$min_fraction,
  minSamples = opt$min_samples,
  binSize = opt$bin_size,
  maxFeatures = opt$max_features,
  ppm = opt$ppm
)

# Find features
XCMSExperiment <- groupChromPeaks(
  object = XCMSExperiment,
  param = DensityParams,
  msLevel = opt$ms_level,
  add = opt$add
)

# Export the XCMSExperiment object to the directory format
saveMsObject(XCMSExperiment, param = PlainTextParam(path = opt$output_path))
