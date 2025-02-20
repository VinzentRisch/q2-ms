#!/usr/bin/env Rscript --vanilla

library(xcms)
library(Spectra)
library(MsExperiment)
library(MsIO)
library(optparse)
library(MSnbase)

# Define command-line options
option_list <- list(
  make_option(opt_str = "--spectra", type = "character"),
  make_option(opt_str = "--xcms_experiment", type = "character"),
  make_option(opt_str = "--ppm", type = "numeric"),
  make_option(opt_str = "--min_peak_width", type = "numeric"),
  make_option(opt_str = "--max_peak_width", type = "numeric"),
  make_option(opt_str = "--sn_thresh", type = "numeric"),
  make_option(opt_str = "--prefilter_k", type = "numeric"),
  make_option(opt_str = "--prefilter_i", type = "numeric"),
  make_option(opt_str = "--mz_center_fun", type = "character"),
  make_option(opt_str = "--integrate", type = "integer"),
  make_option(opt_str = "--mz_diff", type = "numeric"),
  make_option(opt_str = "--fit_gauss", type = "logical"),
  make_option(opt_str = "--noise", type = "numeric"),
  make_option(opt_str = "--first_baseline_check", type = "logical"),
  make_option(opt_str = "--ms_level", type = "integer"),
  make_option(opt_str = "--threads", type = "integer"),
  make_option(opt_str = "--extend_length_msw", type = "logical"),
  make_option(opt_str = "--verbose_columns", type = "logical"),
  make_option(opt_str = "--verbose_beta_columns", type = "logical"),
  make_option(opt_str = "--output_path", type = "character")
)

# Parse arguments
optParser <- OptionParser(option_list = option_list)
opt <- parse_args(optParser)

# Load the XCMSExperiment or MsExperiment
XCMSExperiment <- tryCatch({
    readMsObject(XcmsExperiment(), PlainTextParam(opt$xcms_experiment))
}, error = function(e) {
    readMsObject(MsExperiment(), PlainTextParam(opt$xcms_experiment))
})

# Create paramter object for CentWave
CentWaveParams <- CentWaveParam(
  ppm = opt$ppm,
  peakwidth = c(opt$min_peak_width, opt$max_peak_width),
  snthresh = opt$sn_thresh,
  prefilter = c(opt$prefilter_k, opt$prefilter_i),
  mzCenterFun = opt$mz_center_fun,
  integrate = opt$integrate,
  mzdiff = opt$mz_diff,
  fitgauss = opt$fit_gauss,
  noise = opt$noise,
  firstBaselineCheck = opt$first_baseline_check,
  extendLengthMSW = opt$extend_length_msw,
  verboseColumns = opt$verbose_columns,
  verboseBetaColumns= opt$verbose_beta_columns
)

# Find peaks using the CentWave algorithm
XCMSExperiment <- findChromPeaks(
  object = XCMSExperiment,
  param = CentWaveParams,
  msLevel = opt$ms_level,
  BPPARAM = MulticoreParam(workers = opt$threads)
)

# Export the XCMSExperiment object to the directory format
saveMsObject(XCMSExperiment, param = PlainTextParam(path = opt$output_path))
