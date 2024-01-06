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
from typing import Optional

import pandera as pa
from cobra.flux_analysis import single_gene_deletion
from pandera.typing import Series

from memote.experimental.experiment import Experiment


__all__ = ("EssentialityExperiment",)

LOGGER = logging.getLogger(__name__)


class EssentialityExperimentModel(pa.DataFrameModel):
    gene: Series[str] = pa.Field(
        title="Gene Identifier",
        description="The gene identifier must correspond to the metabolic model "
        "identifiers.",
        unique=True,
    )
    essential: Series[bool] = pa.Field(
        title="Gene Essentiality",
        description="Whether a gene is (conditionally) essential.",
    )
    comment: Optional[Series[str]] = pa.Field(
        nullable=True,
        title="Comment",
        description="Optional comment which is not processed further.",
    )

    class Config:
        coerce = True
        strict = "filter"


class EssentialityExperiment(Experiment):
    """Represent an essentiality experiment."""

    def __init__(self, **kwargs):
        """
        Initialize an essentiality experiment.

        Parameters
        ----------
        kwargs

        """
        super(EssentialityExperiment, self).__init__(**kwargs)

    def validate(self, model, checks=None):
        """Use a defined schema to validate the essentiality table format."""
        EssentialityExperimentModel.validate(self.data, lazy=True)
        assert self.data["gene"].isin({g.id for g in model.genes}).all()

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
