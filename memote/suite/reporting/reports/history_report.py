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
from builtins import dict, str

from memote.suite.reporting.reports.report import Report
import memote.suite.reporting.plot as plt
from memote.suite.reporting.bag import ResultBagWrapper

LOGGER = logging.getLogger(__name__)


class HistoryReport(Report):
    """Render a rich report using the git repository history."""

    _valid_indexes = frozenset(["time", "hash"])

    def __init__(self, repo, directory, index="time", **kwargs):
        """
        Initialize the git interaction and dask bag.

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
        super(HistoryReport, self).__init__(**kwargs)
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
        self.bag.build_index()
        self.index = {
            "time": "timestamp",
            "hash": "commit_hash"
        }.get(index, ValueError("Unknown index type '{}'.".format(index)))
        if isinstance(self.index, ValueError):
            raise self.index

    def render_html(self):
        """Render a rich report for the repository."""
        template = self.env.get_template("history_report.html")
        names = self.bag.get_model_ids()
        return template.render(
            names=names,
            basics=self._collect_basic_plots(),
            biomass=self._collect_biomass_plots()
        )

    def _collect_basic_plots(self):
        """Create plots from the basic info data frame."""
        df = self.bag.get_basic_dataframe()
        plots = dict()
        # create genes plot
        plots["genes"] = plt.scatter_line_chart(
            df[[self.index, "num_genes"]], "Number of Genes")
        # reactions
        plots["reactions"] = plt.scatter_line_chart(
            df[[self.index, "num_reactions"]],
            "Number of Reactions")
        # metabolites
        plots["metabolites"] = plt.scatter_line_chart(
            df[[self.index, "num_metabolites"]],
            "Number of Metabolites")
        plots["metabolites_no_formula"] = plt.scatter_line_chart(
            df[[self.index, "num_metabolites_no_formula"]],
            "Number of Metabolites Without Formula")
        return plots

    def _collect_biomass_plots(self):
        """Create plots from the biomass info data frame."""
        df = self.bag.get_biomass_dataframe()
        plots = dict()
        # components sum
        factor = "reaction"
        plots["biomass_sum"] = plt.scatter_line_chart(
            df[[self.index, "biomass_sum", factor]],
            "Sum of biomass components")
        plots["biomass_default_flux"] = plt.scatter_line_chart(
            df[[self.index, "biomass_default_flux", factor]],
            "Biomass flux")
        plots["num_default_blocked_precursors"] = plt.scatter_line_chart(
            df[[self.index, "num_default_blocked_precursors", factor]],
            "Number of blocked biomass precursors in default medium.")
        plots["num_open_blocked_precursors"] = plt.scatter_line_chart(
            df[[self.index, "num_open_blocked_precursors", factor]],
            "Number of blocked biomass precursors in complete medium.")
        return plots
