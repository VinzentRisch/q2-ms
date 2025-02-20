# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import json
import os
import sys

import pandas as pd
import pymzml
from qiime2.core.exceptions import ValidationError
from qiime2.plugin import model


class mzMLFormat(model.TextFileFormat):
    def _validate(self, n_records=None):
        try:
            # Suppressing warning print "Not index found and build_index_from_scratch
            # is False". This could also be solved with setting build_index_from_scratch
            # to True but this builds the index and slows down validation.
            sys.stdout = open(os.devnull, "w")
            pymzml.run.Reader(str(self))
            sys.stdout = sys.__stdout__
        except Exception as e:
            raise ValidationError(e)

    def _validate_(self, level):
        self._validate()


class mzMLDirFmt(model.DirectoryFormat):
    mzml = model.FileCollection(r".*\.mzML$", format=mzMLFormat)

    @mzml.set_path_maker
    def mzml_path_maker(self, sample_id):
        return f"{sample_id}.mzML"


class MSBackendDataFormat(model.TextFileFormat):
    def _validate(self):
        header_exp = [
            "msLevel",
            "rtime",
            "acquisitionNum",
            "dataOrigin",
            "polarity",
            "precScanNum",
            "precursorMz",
            "precursorIntensity",
            "precursorCharge",
            "collisionEnergy",
            "peaksCount",
            "totIonCurrent",
            "basePeakMZ",
            "basePeakIntensity",
            "ionisationEnergy",
            "lowMZ",
            "highMZ",
            "injectionTime",
            "spectrumId",
            "dataStorage",
            "scanIndex",
        ]

        header_obs_1 = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()
        header_obs_2 = pd.read_csv(
            str(self), sep="\t", skiprows=1, nrows=1
        ).columns.tolist()

        if (not set(header_exp).issubset(set(header_obs_2))) or header_obs_1[
            0
        ] != "# MsBackendMzR":
            raise ValidationError(
                "Header does not match MSBackendDataFormat. It must consist of the "
                "following two line with at least these columns:\n"
                "# MsBackendMzR\n" + "\t".join(header_exp) + "\n\nFound instead:\n"
                f"{header_obs_1[0]}\n" + "\t".join(header_obs_2)
            )

    def _validate_(self, level):
        self._validate()


class MSExperimentLinkMColsFormat(model.TextFileFormat):
    def _validate(self):
        with open(str(self), "r") as file:
            first_line = file.readline().strip()

        if first_line != '"subsetBy"':
            raise ValidationError(
                "Header does not match MSExperimentLinkMColsFormat. It must "
                "consist of the following line:\n"
                '"subsetBy"\n\n'
                "Found instead:\n"
                f"{first_line}"
            )

    def _validate_(self, level):
        self._validate()


class MSExperimentSampleDataLinksSpectra(model.TextFileFormat):
    def _validate(self):
        first_line = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()

        if len(first_line) != 2:
            raise ValidationError(
                "File does not match MSExperimentLinkMColsFormat. "
                "It must consist of exactly two columns."
            )

    def _validate_(self, level):
        self._validate()


class MSExperimentSampleDataFormat(model.TextFileFormat):
    def _validate(self):
        header_obs = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()

        if "spectraOrigin" not in header_obs:
            raise ValidationError(
                "Header does not match MSExperimentSampleDataFormat. It must consist "
                "of at least two columns where one is called 'spectraOrigin':"
                + "\n\nFound instead:\n"
                + ", ".join(header_obs)
            )

    def _validate_(self, level):
        self._validate()


class XCMSExperimentJSONFormat(model.TextFileFormat):
    def _validate(self):
        try:
            with self.open() as file:
                content = file.read()
            data = json.loads(content)

            if not isinstance(data, list):
                raise ValidationError(
                    "File does not match XCMSExperimentJSONFormat. "
                    "The root element must be a list."
                )

            parsed_item = json.loads(data[0])

            required_keys = {"type", "attributes", "value"}
            if not required_keys.issubset(parsed_item.keys()):
                raise ValidationError(
                    "File does not match XCMSExperimentJSONFormat. "
                    "JSON object must contain the keys: " + ", ".join(required_keys)
                )

        except json.JSONDecodeError as e:
            raise ValidationError(f"File is not valid JSON: {e}")

    def _validate_(self, level):
        self._validate()


class SpectraSlotsFormat(model.TextFileFormat):
    def _validate(self):
        expected_keys = {
            "processingQueueVariables",
            "processing",
            "processingChunkSize",
            "backend",
        }

        with self.open() as file:
            lines = file.readlines()

        keys = set()
        for line in lines:
            if "=" not in line:
                continue

            key = line.split("=", 1)[0].strip()
            keys.add(key)

        if keys != expected_keys:
            raise ValidationError(
                "File does not match SpectraSlotsFormat. "
                "File must have the following structure:\n"
                "processingQueueVariables = ...\n"
                "processing = ...\n"
                "processingChunkSize = ...\n"
                "backend = ...\n"
            )

    def _validate_(self, level):
        self._validate()


class XCMSExperimentChromPeakDataFormat(model.TextFileFormat):
    def _validate(self):
        header_exp = ["ms_level", "is_filled"]
        header_obs = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()

        if header_exp != header_obs:
            raise ValidationError(
                "Header does not match XCMSExperimentChromPeakDataFormat. It must "
                "consist of the following columns:\n"
                + ", ".join(header_exp)
                + "\n\nFound instead:\n"
                + ", ".join(header_obs)
            )

    def _validate_(self, level):
        self._validate()


class XCMSExperimentChromPeaksFormat(model.TextFileFormat):
    def _validate(self):
        header_exp = [
            "mz",
            "mzmin",
            "mzmax",
            "rt",
            "rtmin",
            "rtmax",
            "into",
            "intb",
            "maxo",
            "sn",
            "sample",
        ]
        header_obs = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()

        if not set(header_exp).issubset(set(header_obs)):
            raise ValidationError(
                "Header does not match XCMSExperimentChromPeaksFormat. It must at least"
                "consist of the following columns:\n"
                + ", ".join(header_exp)
                + "\n\nFound instead:\n"
                + ", ".join(header_obs)
            )

    def _validate_(self, level):
        self._validate()


class XCMSExperimentFeatureDefinitionsFormat(model.TextFileFormat):
    def _validate(self):
        header_exp = [
            "mzmed",
            "mzmin",
            "mzmax",
            "rtmed",
            "rtmin",
            "rtmax",
            "npeaks",
            "peakidx",
            "ms_level",
        ]
        header_obs = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()

        if not set(header_exp).issubset(set(header_obs)):
            raise ValidationError(
                "Header does not match XCMSExperimentFeatureDefinitionsFormat. It must "
                "at least consist of the following columns:\n"
                + ", ".join(header_exp)
                + "\n\nFound instead:\n"
                + ", ".join(header_obs)
            )

    def _validate_(self, level):
        self._validate()


class XCMSExperimentFeaturePeakIndexFormat(model.TextFileFormat):
    def _validate(self):
        header_exp = ["feature_index", "peak_index"]
        header_obs = pd.read_csv(str(self), sep="\t", nrows=0).columns.tolist()

        if header_exp != header_obs:
            raise ValidationError(
                "Header does not match XCMSExperimentFeaturePeakIndexFormat. It must "
                "consist of the following columns:\n"
                + ", ".join(header_exp)
                + "\n\nFound instead:\n"
                + ", ".join(header_obs)
            )

    def _validate_(self, level):
        self._validate()


class XCMSExperimentDirFmt(model.DirectoryFormat):
    ms_backend_data = model.File(
        pathspec="ms_backend_data.txt",
        format=MSBackendDataFormat,
    )
    ms_experiment_link_mcols = model.File(
        pathspec="ms_experiment_link_mcols.txt",
        format=MSExperimentLinkMColsFormat,
    )
    ms_experiment_sample_data_links_spectra = model.File(
        pathspec="ms_experiment_sample_data_links_spectra.txt",
        format=MSExperimentSampleDataLinksSpectra,
    )
    ms_experiment_sample_data = model.File(
        pathspec="ms_experiment_sample_data.txt",
        format=MSExperimentSampleDataFormat,
    )
    spectra_processing_queue = model.File(
        pathspec="spectra_processing_queue.json",
        format=XCMSExperimentJSONFormat,
    )
    spectra_slots = model.File(
        pathspec="spectra_slots.txt",
        format=SpectraSlotsFormat,
    )
    xcms_experiment_process_history = model.File(
        pathspec="xcms_experiment_process_history.json",
        format=XCMSExperimentJSONFormat,
        optional=True,
    )
    xcms_experiment_chrom_peak_data = model.File(
        pathspec="xcms_experiment_chrom_peak_data.txt",
        format=XCMSExperimentChromPeakDataFormat,
        optional=True,
    )
    xcms_experiment_chrom_peaks = model.File(
        pathspec="xcms_experiment_chrom_peaks.txt",
        format=XCMSExperimentChromPeaksFormat,
        optional=True,
    )
    xcms_experiment_feature_definitions = model.File(
        pathspec="xcms_experiment_feature_definitions.txt",
        format=XCMSExperimentFeatureDefinitionsFormat,
        optional=True,
    )
    xcms_experiment_feature_peak_index = model.File(
        pathspec="xcms_experiment_feature_peak_index.txt",
        format=XCMSExperimentFeaturePeakIndexFormat,
        optional=True,
    )
