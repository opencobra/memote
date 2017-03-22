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

import logging
from os.path import join
from builtins import dict
from uuid import uuid4

from jinja2 import Environment, PackageLoader, select_autoescape

import memote.suite.reporting.plot as plt
from memote.suite.reporting.bag import ResultBagWrapper

LOGGER = logging.getLogger(__name__)


class Report(object):
    """Render a basic report from the given data."""

    def __init__(self, data=None, **kwargs):
        """Initialize the Jinja2 environment and data."""
        super(Report, self).__init__(**kwargs)
        self.env = Environment(
            loader=PackageLoader("memote.suite.reporting", "templates"),
            autoescape=select_autoescape(["html", "xml"])
        )
        self.data = data

    def render_html(self):
        """Render a one-shot report for a model."""
        template = self.env.get_template("basic.html")
        return template.render(
            name=self.data["report"]["test_basic"]["model_id"],
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
        self.history.insert(0, self.latest.hexsha)
        self.directory = directory
        self.files = [join(self.directory, "{}.json".format(commit))
                      for commit in self.history]
        if len(self.files) == 0:
            raise RuntimeError(
                "The given directory '{}' contains no JSON files."
                " Cannot generate a report.".format(self.directory))
        self.bag = ResultBagWrapper(self.files)
        self.bag.build_index(index)

    def render_html(self):
        """Render a rich report for the repository."""
        template = self.env.get_template("git_enabled.html")
        names = self.bag.get_model_ids()
        (basic_specs, basic_uuids) = self._collect_basic_specs()
        return template.render(
            names=names,
            basic_specs=basic_specs,
            basic_uuids=basic_uuids
        )

    def _collect_basic_specs(self):
        """Collect Vega specs from a data frame."""
        df = self.bag.get_basic_dataframe()
        # Reverse order since git history ranges from latest to oldest but
        # for plotting oldest to newest is preferred.
        df = df.iloc[::-1]
        specs = dict()
        uuids = dict()
        # create gene spec
        specs["genes"] = plt.scatter_line_chart(
            df[["x", "num_genes"]], "num_genes:Q", "Number of Genes",
            **self.bag.axis_description)
        uuids["genes"] = "uuid_" + uuid4().hex
        # reactions
        specs["reactions"] = plt.scatter_line_chart(
            df[["x", "num_reactions"]], "num_reactions:Q",
            "Number of Reactions", **self.bag.axis_description)
        uuids["reactions"] = "uuid_" + uuid4().hex
        # metabolites
        specs["metabolites"] = plt.scatter_line_chart(
            df[["x", "num_metabolites"]], "num_metabolites:Q",
            "Number of Metabolites", **self.bag.axis_description)
        uuids["metabolites"] = "uuid_" + uuid4().hex
        return (specs, uuids)
