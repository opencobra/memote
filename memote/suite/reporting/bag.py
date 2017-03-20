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

"""Utilities that handle a `dask.bag`."""

from __future__ import absolute_import

import io
import logging
try:
    import simplejson as json
except ImportError:
    import json
from os.path import exists

import pandas as pd
import dask.bag as db
from colorama import Fore

LOGGER = logging.getLogger(__name__)


class ResultBagWrapper(object):
    """
    Report-specific wrapper around a `dask.bag`.

    Attributes
    ----------
    axis_description : dict
        Can be passed as keyword arguments to Altair plotting functions to
        describe the x-axis.
    """

    def __init__(self, files, **kwargs):
        """
        Load (JSON) documents into memory managed by a `dask.bag`.

        The order of the `files` argument determines the order of rows in data
        frames returned by other methods.

        Parameters
        ----------
        files : iterable
            A list of filenames that should contain valid JSON.
        """
        super(ResultBagWrapper, self).__init__(**kwargs)
        # load all into memory and avoid strange dask JSON object expectations
        objects = list()
        for filename in files:
            if not exists(filename):
                LOGGER.warn(
                    Fore.YELLOW +
                    "Expected file %s is missing."
                    + Fore.RESET, filename)  # noqa: W503
                continue
            with io.open(filename) as file_h:
                objects.append(json.load(file_h))
        self._bag = db.from_sequence(objects)
        self._index = None
        self.axis_description = None

    def build_index(self, dimension):
        """Build a data index either from timestamps or commit hashes."""
        if dimension == "time":
            self._build_time_index()
        elif dimension == "hash":
            self._build_commit_index()
        else:
            raise ValueError("Unknown index dimension '{}'".format(dimension))

    def _build_time_index(self):
        """Build an index from timestamps."""
        self._index = pd.Series(
            list(self._bag.pluck("meta", dict()).pluck("timestamp")),
            dtype="datetime64[ns]")
        self.axis_description = dict(x_axis="x:T", x_title="Timestamp")

    def _build_commit_index(self):
        """Build an index from commit hashes."""
        series = pd.Series(
            list(self._bag.pluck("meta", dict()).pluck("commit_hash")),
            dtype="str")
        trunc = 5
        res = series.str[:trunc]
        while len(res.unique()) < len(series):
            trunc += 1
            res = series.str[:trunc]
        self._index = res
        self.axis_description = dict(x_axis="x:O", x_title="Commit Hash")

    def get_model_ids(self):
        """Get unique model IDs. Should normally be of length one."""
        return self._bag.pluck("report").pluck("memote.suite.test_basic").\
            pluck("model_id").distinct().compute()

    def get_basic_dataframe(self):
        """Collect results from `test_basic`."""
        columns = ["num_genes", "num_reactions", "num_metabolites"]
        data_types = ["int", "int", "int"]
        expected = pd.DataFrame({col: pd.Series(dtype=dt)
                                 for (col, dt) in zip(columns, data_types)})
        df = self._bag.pluck("report", dict()).\
            pluck("memote.suite.test_basic", dict()).\
            to_dataframe(expected).compute()
        df.index = self._index
        df["x"] = df.index
        return df
