# -*- coding: utf-8 -*-

# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Modules related to reading and writing files."""

from __future__ import absolute_import

import pandas as pd


def read_tabular(filename, dtype_conversion=None):
    """
    Read a tabular data file which can be CSV, TSV, XLS or XLSX.

    Parameters
    ----------
    filename : str or pathlib.Path
        The full file path. May be a compressed file.
    dtype_conversion : dict
        Column names as keys and corresponding type for loading the data.
        Please take a look at the `pandas documentation
        <https://pandas.pydata.org/pandas-docs/stable/io.html#specifying-column-data-types>`__
        for detailed explanations.

    Returns
    -------
    pandas.DataFrame
        The data table.

    """
    if dtype_conversion is None:
        dtype_conversion = {}
    name, ext = filename.split(".", 1)
    ext = ext.lower()
    # Completely empty columns are interpreted as float by default.
    dtype_conversion["comment"] = str
    if "csv" in ext:
        df = pd.read_csv(filename, dtype=dtype_conversion, encoding="utf-8")
    elif "tsv" in ext:
        df = pd.read_table(filename, sep="\t", dtype=dtype_conversion, encoding="utf-8")
    elif "xlsx" in ext:
        df = pd.read_excel(filename, dtype=dtype_conversion, engine="openpyxl")
    elif "xls" in ext:
        df = pd.read_excel(filename, dtype=dtype_conversion, engine="xlrd")
    elif "ods" in ext:
        df = pd.read_excel(filename, dtype=dtype_conversion)
    else:
        raise ValueError("Unknown file format '{}'.".format(ext))
    return df
