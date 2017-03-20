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

"""Render results into pretty HTML."""

from __future__ import absolute_import

import io
import logging
try:
    import simplejson as json
except ImportError:
    import json
from os.path import join, exists
from builtins import dict
from uuid import uuid4

import pandas as pd
import dask.bag as db
from jinja2 import Environment, PackageLoader, select_autoescape
from colorama import Fore

import memote.suite.plots as plt

LOGGER = logging.getLogger(__name__)


class Report(object):
    """Render a basic report from the given data."""

    def __init__(self, data=None, **kwargs):
        """Initialize the Jinja2 environment and data."""
        super(Report, self).__init__(**kwargs)
        self.env = Environment(
            loader=PackageLoader("memote.suite", "templates"),
            autoescape=select_autoescape(["html", "xml"])
        )
        self.data = data

    def render_html(self):
        """Render a one-shot report for a model."""
        template = self.env.get_template("basic.html")
        return template.render(
            name=self.data["report"]["memote.suite.test_basic"]["model_id"],
            timestamp=self.data["meta"]["timestamp"],
            data=self.data)


class GitEnabledReport(Report):
    """Render a rich report using the git repository history."""

    _valid_indexes = frozenset(["time", "hash"])

    def __init__(self, repo, directory, index="time", **kwargs):
        """
        Initialize the Jinja2 environment and data.

        Paramters
        ---------
        repo : git.Repo
            Instance of the working directory git repository.
        directory : str or path
            Where previously collected test results can be found.
        index : {'time', 'hash'}, optional
            Whether to use time (the default) or commit hashes as the default
            axis in plots.
        """
        super(GitEnabledReport, self).__init__(**kwargs)
        self.index_dim = index.lower()
        if self.index_dim not in self._valid_indexes:
            raise ValueError(
                "Given index '{0}' must be one of {1}."
                "".format(self.index_dim, str(self._valid_indexes)))
        self.repo = repo
        self.latest = self.repo.active_branch.commit
        self.history = [commit.hexsha for commit in self.latest.iter_parents()]
        self.directory = directory
        self.bag = self._collect_bag()
        self.index_args = None
        self.index = self._build_index()

    def render_html(self):
        """Render a rich report for the repository."""
        template = self.env.get_template("git_enabled.html")
        names = self.bag.pluck("report").pluck("memote.suite.test_basic").\
                pluck("model_id").distinct().compute()
        specs = dict()
        uuids = dict()
        (basic_specs, basic_uuids) = self._get_basics()
        specs.update(basic_specs)
        uuids.update(basic_uuids)
        return template.render(
            names=names,
            specs=specs,
            uuids=uuids
        )

    def _collect_bag(self):
        """Collect all data into a dask bag."""
        # load all into memory and avoid strange dask JSON object expectation
        objects = list()
        for commit in self.history:
            filename = join(self.directory, "{}.json".format(commit))
            if not exists(filename):
                LOGGER.warn(
                    Fore.YELLOW +
                    "Results for commit %s are missing."
                    + Fore.RESET, commit)
                continue
            with io.open(filename, "r") as file_h:
                objects.append(json.load(file_h))
        return db.from_sequence(objects)

    def _build_index(self):
        """Collect basic information from the bag into a data frame."""
        if self.index_dim == "time":
            self.index_args = dict(x_axis="x:T", x_title="Timestamp")
            return pd.Series(
                list(self.bag.pluck("meta", dict()).pluck("timestamp")),
                dtype="datetime64[ns]")
        elif self.index_dim == "hash":
            self.index_args = dict(x_axis="x:O", x_title="Commit Hash")
            series = pd.Series(
                list(self.bag.pluck("meta", dict()).pluck("commit_hash")),
                dtype="str")
            return series.str[:7]  # trust that hashes are unique
        else:
            raise ValueError(
                "Unknown index dimension '{}'".format(self.index_dim))

    def _get_basics(self):
        """Collect basic information from the bag into a data frame."""
#        columns = ["commit_hash", "timestamp"]
#        data_types = ["str", "datetime64[ns]"]
#        expected = pd.DataFrame({col: pd.Series(dtype=dt)
#                                 for (col, dt) in zip(columns, data_types)})
        df = self.bag.pluck("report", dict()).\
            pluck("memote.suite.test_basic", dict()).\
            to_dataframe().compute()
        df.index = self.index
        df["x"] = df.index
        df.sort_index(inplace=True)
        specs = dict()
        uuids = dict()
        # create gene spec
        specs["genes"] = plt.scatter_line_chart(
            df[["x", "num_genes"]], "num_genes:Q", "Number of Genes",
            **self.index_args)
        uuids["genes"] = "uuid" + uuid4().hex
        # reactions
        specs["reactions"] = plt.scatter_line_chart(
            df[["x", "num_reactions"]], "num_reactions:Q",
            "Number of Reactions", **self.index_args)
        uuids["reactions"] = "uuid" + uuid4().hex
        # metabolites
        specs["metabolites"] = plt.scatter_line_chart(
            df[["x", "num_metabolites"]], "num_metabolites:Q",
            "Number of Metabolites", **self.index_args)
        uuids["metabolites"] = "uuid" + uuid4().hex
        return (specs, uuids)
