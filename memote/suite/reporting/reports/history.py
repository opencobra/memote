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

    def __init__(self, repository, directory, index="time", **kwargs):
        """
        Initialize the git interaction and dask bag.

        Parameters
        ----------
        repository : git.Repo
            An instance of the working directory git repository.
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
        self.repo = repository
        self.latest = self.repo.active_branch.commit
        self.history = [commit.hexsha for commit in self.latest.iter_parents()]
        self.history.insert(0, self.latest.hexsha)
        self.directory = directory
        self.files = [join(self.directory, "{}.json".format(commit))
                      for commit in self.history]
        if len(self.files) == 0:
            raise RuntimeError("There is no git branch history!")
        self.bag = ResultBagWrapper(self.files)
        self.bag.build_index()
        self.index = {
            "time": "timestamp",
            "hash": "commit_hash"
        }.get(index, ValueError("Unknown index type '{}'.".format(index)))
        if isinstance(self.index, ValueError):
            raise self.index

    def render_html(self):
        """
        Render a rich report for the repository.

        This is currently a stub while we convert from ``jinja2`` templates
        to a full Angular based report.
        """
        return u""

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
        plots["metabolites_no_charge"] = plt.scatter_line_chart(
            df[[self.index, "metabolites_no_charge"]],
            "Number of Metabolites Without Charge")
        plots["reactions_no_GPR"] = plt.scatter_line_chart(
            df[[self.index, "reactions_no_GPR"]],
            "Number of Reactions Without GPR Rule")
#        plots["metabolic_coverage"] = plt.scatter_line_chart(
#            df[[self.index, "metabolic_coverage"]],
#            "Metabolic Coverage")
        plots["ngam_reaction"] = plt.scatter_line_chart(
            df[[self.index, "ngam_reaction"]],
            "Number of Non-growth-associated Maintenance Reactions")
        return plots

    def _collect_consistency_plots(self):
        """Create plots from the consistency info data frame."""
        df = self.bag.get_consistency_dataframe()
        plots = dict()
        plots["is_consistent"] = plt.boolean_chart(
            df[[self.index, "is_consistent"]],
            "Is Stoichiometrically Consistent")
        plots["unconserved_metabolites"] = plt.scatter_line_chart(
            df[[self.index, "unconserved_metabolites"]],
            "Number of Unconserved Metabolites")
        plots["magic_atp_production"] = plt.boolean_chart(
            df[[self.index, "magic_atp_production"]],
            "Has Magic ATP Production")
        plots["imbalanced_reactions"] = plt.scatter_line_chart(
            df[[self.index, "imbalanced_reactions"]],
            "Number of Imbalanced Reactions")
        plots["blocked_reactions"] = plt.scatter_line_chart(
            df[[self.index, "blocked_reactions"]],
            "Number of Blocked Reactions")
        # TODO: Fix looped in tests.
#        plots["looped_reactions"] = plt.scatter_line_chart(
#            df[[self.index, "looped_reactions"]],
#            "Number of Looped Reactions")
        return plots

    def _collect_syntax_plots(self):
        """Create plots from the syntax info data frame."""
        df = self.bag.get_consistency_dataframe()
        plots = dict()
#        plots["reaction_compartment_suffix"] = plt.scatter_line_chart(
#            df[[self.index, "reaction_compartment_suffix"]],
#            "Number of Reactions with Wrong Compartment Tag")
#        plots["untagged_normal_transport"] = plt.scatter_line_chart(
#            df[[self.index, "untagged_normal_transport"]],
#            "Number of Transport Reactions with Wrong Tag")
#        plots["untagged_abc_transport"] = plt.scatter_line_chart(
#            df[[self.index, "untagged_abc_transport"]],
#            "Number of ABC Transport Reactions with Wrong Tag")
#        plots["uppercase_metabolites"] = plt.scatter_line_chart(
#            df[[self.index, "uppercase_metabolites"]],
#            "Number of Uppercase Metabolite Identifiers")
        plots["untagged_demand"] = plt.scatter_line_chart(
            df[[self.index, "untagged_demand"]],
            "Number of Wrongly Labelled Demand Reactions")
        plots["false_demand"] = plt.scatter_line_chart(
            df[[self.index, "false_demand"]],
            "Number of Falsely Labelled Demand Reactions")
        plots["untagged_sink"] = plt.scatter_line_chart(
            df[[self.index, "untagged_sink"]],
            "Number of Wrongly Labelled Sink Reactions")
        plots["false_sink"] = plt.scatter_line_chart(
            df[[self.index, "false_sink"]],
            "Number of Falsely Labelled Sink Reactions")
        plots["untagged_exchange"] = plt.scatter_line_chart(
            df[[self.index, "untagged_exchange"]],
            "Number of Wrongly Labelled Exchange Reactions")
        plots["false_exchange"] = plt.scatter_line_chart(
            df[[self.index, "false_exchange"]],
            "Number of Falsely Labelled Exchange Reactions")
        return plots

    def _collect_biomass_plots(self):
        """Create plots from the biomass info data frame."""
        df = self.bag.get_biomass_dataframe()
        plots = dict()
        # components sum
        factor = "biomass_ids"
        plots["biomass_sum"] = plt.scatter_line_chart(
            df[[self.index, "biomass_sum", factor]],
            r"$ \text{Sum of Biomass Components }"
            r"[ \text{mmol} \text{g}_{\text{DW}}^{-1}  \text{h}^{-1} ] $")
        plots["biomass_default_flux"] = plt.scatter_line_chart(
            df[[self.index, "biomass_default_flux", factor]],
            r"$ \text{Biomass Flux }"
            r"[ \text{mmol} \text{g}_{\text{DW}}^{-1}  \text{h}^{-1} ] $")
        plots["num_default_blocked_precursors"] = plt.scatter_line_chart(
            df[[self.index, "num_default_blocked_precursors", factor]],
            "Number of Blocked Biomass Precursors in Default Medium")
        plots["num_open_blocked_precursors"] = plt.scatter_line_chart(
            df[[self.index, "num_open_blocked_precursors", factor]],
            "Number of Blocked Biomass Precursors in Complete Medium")
        plots["gam_in_biomass"] = plt.boolean_chart(
            df[[self.index, "gam_in_biomass"]],
            "Biomass Contains Growth-associated Maintenance")
        return plots

    def _collect_annotation_plots(self):
        """Create plots from the annotation info data frame."""
        pass
