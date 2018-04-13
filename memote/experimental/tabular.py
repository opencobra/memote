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


def read_tabular(filename):
    """
    Read a tabular data file which can be CSV, TSV, XLS, XLSX, or ODS.

    Parameters
    ----------
    filename : str or pathlib.Path
        The full file path. May be a compressed file.

    Returns
    -------
    pandas.DataFrame
        The data table.

    """
    name, ext = filename.split(".", 1)
    ext = ext.lower()
    # Completely empty columns are interpreted as float by default.
    if "csv" in ext:
        df = pd.read_csv(filename, dtype={"comment": str}, encoding="utf-8")
    elif "tsv" in ext:
        df = pd.read_table(filename, dtype={"comment": str}, encoding="utf-8")
    elif "xls" in ext or "xlsx" in ext:
        df = pd.read_excel(filename, dtype={"comment": str}, encoding="utf-8")
    # TODO: Add a function to parse ODS data into a pandas data frame.
    else:
        raise ValueError("Unknown file format '{}'.".format(ext))
    return df
