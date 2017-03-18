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
from builtins import dict, zip

import pandas as pd
import dask.bag as db
from jinja2 import Environment, PackageLoader, select_autoescape, Markup
from colorama import Fore

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
        self.directory = directory
        self.bag = self._collect_bag()
        self.index = self._build_index()

    def render_html(self):
        """Render a rich report for the repository."""
        template = self.env.get_template("git_enabled.html")
        return template.render(
            names=self.bag.pluck("report").pluck("memote.suite.test_basic").
                pluck("model_id").distinct().compute(),
            meta=Markup(self._get_basics_df().to_html())
            )

    def _collect_bag(self):
        """Collect all data into a dask bag."""
        # load all into memory and avoid strange dask JSON object expectation
        objects = list()
        for commit in self.latest.iter_parents():
            filename = join(self.directory, "{}.json".format(commit.hexsha))
            if not exists(filename):
                LOGGER.warn(
                    Fore.YELLOW +
                    "Results for commit %s are missing."
                    + Fore.RESET, commit.hexsha)
                continue
            with io.open(filename, "r") as file_h:
                objects.append(json.load(file_h))
        return db.from_sequence(objects)

    def _build_index(self):
        """Collect basic information from the bag into a data frame."""
        column = dict(hash="commit_hash", time="timestamp")
        data_type = dict(hash="str", time="datetime64[ns]")
        return pd.Series(
            self.bag.pluck("meta", dict()).pluck(column[self.index_dim]),
            dtype=data_type[self.index_dim])

    def _get_basics_df(self):
        """Collect basic information from the bag into a data frame."""
        columns = ["commit_hash", "timestamp"]
        data_types = ["str", "datetime64[ns]"]
        expected = pd.DataFrame({col: pd.Series(dtype=dt)
                                 for (col, dt) in zip(columns, data_types)})
        return self.bag.pluck("meta").to_dataframe(expected).compute()
