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
  make_option(opt_str = "--threads", type = "integer"),
  make_option(opt_str = "--output_path", type = "character"),
  make_option(opt_str = "--ms_level", type = "integer")
)

# Parse arguments
optParser <- OptionParser(option_list = option_list)
opt <- parse_args(optParser)

XCMSExperiment <- readMsObject(XcmsExperiment(), PlainTextParam(opt$xcms_experiment))

# Set parameters
DensityParams <- PeakDensityParam(
  sampleGroups = sampleData(XCMSExperiment)$samplegroup,
  bw = opt$bw,
  minFraction = opt$min_fraction,
  minSamples = opt$min_samples,
  binSize = opt$bin_size,
  maxFeatures = opt$max_features
)


# Adjust retention time using the Obiwarp algorithm
XCMSExperiment <- groupChromPeaks(
  object = XCMSExperiment,
  param = DensityParams,
  msLevel = opt$ms_level,
)

# Export the XCMSExperiment object to the directory format
saveMsObject(XCMSExperiment, param = PlainTextParam(path = opt$output_path))
