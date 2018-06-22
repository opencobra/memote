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

from pandas import DataFrame

from memote.experimental.experiment import Experiment

__all__ = ("GrowthExperiment",)

LOGGER = logging.getLogger(__name__)


class GrowthExperiment(Experiment):
    """Represent a growth experiment."""

    SCHEMA = "growth.json"

    def __init__(self, **kwargs):
        """
        Initialize a growth experiment.

        Parameters
        ----------
        kwargs

        """
        super(GrowthExperiment, self).__init__(**kwargs)

    def evaluate(self, model, threshold=0.1):
        """Evaluate in silico growth rates."""
        with model:
            if self.medium is not None:
                self.medium.apply(model)
            if self.objective is not None:
                model.objective = self.objective
            model.add_cons_vars(self.constraints)
            threshold *= model.slim_optimize()
            growth = list()
            for row in self.data.itertuples(index=False):
                with model:
                    exchange = model.reactions.get_by_id(row.exchange)
                    if bool(exchange.reactants):
                        exchange.lower_bound = -row.uptake
                    else:
                        exchange.upper_bound = row.uptake
                    growth.append(model.slim_optimize() >= threshold)
        return DataFrame({
            "exchange": self.data["exchange"],
            "growth": growth
        })
