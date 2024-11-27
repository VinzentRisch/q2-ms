# flake8: noqa
# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from . import _version

__version__ = _version.get_versions()["version"]

importlib.import_module("q2_ms.types")
