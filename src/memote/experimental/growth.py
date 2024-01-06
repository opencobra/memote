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

"""Provide an interface for growth experiments."""

from __future__ import absolute_import

import logging
from typing import Optional

import pandera as pa
from pandas import DataFrame
from pandera.typing import Series

from memote.experimental.experiment import Experiment


__all__ = ("GrowthExperiment",)

LOGGER = logging.getLogger(__name__)


class GrowthExperimentModel(pa.DataFrameModel):
    exchange: Series[str] = pa.Field(
        description="The exchange reaction identifier of the variable medium "
        "component. Typically, this is a carbon source which will be added to a "
        "configured base medium.",
        title="Exchange Reaction Identifier",
    )
    uptake: Series[float] = pa.Field(
        ge=0.0,
        le=1000.0,
        title="Uptake Rate",
        description="The uptake rate for the exchange reaction. For models following "
        "common practices this modifies the lower bound.",
    )
    growth: Series[bool] = pa.Field(
        title="Growth",
        description="A binary indicator whether growth was observed according to the "
        "processed biolog data.",
    )
    comment: Optional[Series[str]] = pa.Field(
        nullable=True,
        title="Comment",
        description="Optional comment which is not processed further.",
    )

    class Config:
        coerce = True
        strict = "filter"


class GrowthExperiment(Experiment):
    """Represent a growth experiment."""

    def __init__(self, **kwargs):
        """
        Initialize a growth experiment.

        Parameters
        ----------
        kwargs

        """
        super(GrowthExperiment, self).__init__(**kwargs)

    def validate(self, model):
        """Use a defined schema to validate the growth table format."""
        GrowthExperimentModel.validate(self.data, lazy=True)

    def evaluate(self, model):
        """Evaluate in silico growth rates."""
        with model:
            if self.medium is not None:
                self.medium.apply(model)
            if self.objective is not None:
                model.objective = self.objective
            model.add_cons_vars(self.constraints)
            growth = list()
            for row in self.data.itertuples(index=False):
                with model:
                    exchange = model.reactions.get_by_id(row.exchange)
                    if bool(exchange.reactants):
                        exchange.lower_bound = -row.uptake
                    else:
                        exchange.upper_bound = row.uptake
                    growth.append(model.slim_optimize() >= self.minimal_growth_rate)
        return DataFrame({"exchange": self.data["exchange"], "growth": growth})
