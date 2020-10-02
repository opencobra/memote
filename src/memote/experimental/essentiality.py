# -*- coding: utf-8 -*-

# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Provide an interface for essentiality experiments."""

from __future__ import absolute_import

import logging

from cobra.flux_analysis import single_gene_deletion

from memote.experimental.experiment import Experiment


__all__ = ("EssentialityExperiment",)

LOGGER = logging.getLogger(__name__)


class EssentialityExperiment(Experiment):
    """Represent an essentiality experiment."""

    SCHEMA = "essentiality.json"

    def __init__(self, **kwargs):
        """
        Initialize an essentiality experiment.

        Parameters
        ----------
        kwargs

        """
        super(EssentialityExperiment, self).__init__(**kwargs)

    def load(self, dtype_conversion=None):
        """
        Load the data table and corresponding validation schema.

        Parameters
        ----------
        dtype_conversion : dict
            Column names as keys and corresponding type for loading the data.
            Please take a look at the `pandas documentation
            <https://pandas.pydata.org/pandas-docs/stable/io.html#specifying-column-data-types>`__
            for detailed explanations.

        """
        if dtype_conversion is None:
            dtype_conversion = {"essential": str}
        super(EssentialityExperiment, self).load(dtype_conversion=dtype_conversion)
        self.data["essential"] = self.data["essential"].isin(self.TRUTHY)

    def validate(self, model, checks=None):
        """Use a defined schema to validate the medium table format."""
        if checks is None:
            checks = []
        custom = [
            {
                "unknown-identifier": {
                    "column": "gene",
                    "identifiers": {g.id for g in model.genes},
                }
            }
        ]
        super(EssentialityExperiment, self).validate(
            model=model, checks=checks + custom
        )

    def evaluate(self, model):
        """Use the defined parameters to predict single gene essentiality."""
        with model:
            if self.medium is not None:
                self.medium.apply(model)
            if self.objective is not None:
                model.objective = self.objective
            model.add_cons_vars(self.constraints)
            essen = single_gene_deletion(
                model, gene_list=self.data["gene"], processes=1
            )
        essen["gene"] = [list(g)[0] for g in essen["ids"]]
        essen["essential"] = (essen["growth"] < self.minimal_growth_rate) | essen[
            "growth"
        ].isna()
        return essen
