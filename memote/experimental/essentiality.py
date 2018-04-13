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
from memote.experimental.checks import check_partial, gene_id_check


__all__ = ("EssentialityExperiment",)

LOGGER = logging.getLogger(__name__)


class EssentialityExperiment(Experiment):
    """Represent an essentiality experiment."""

    SCHEMA = "essentiality.json"

    def __init__(self, obj, **kwargs):
        """
        Initialize an essentiality experiment.

        Parameters
        ----------
        obj : dict
        kwargs

        """
        super(EssentialityExperiment, self).__init__(obj=obj, **kwargs)
        self.medium = obj.get("medium")

    def validate(self, model, checks=[]):
        """Use a defined schema to validate the medium table format."""
        custom = [
            check_partial(gene_id_check, frozenset(g.id for g in model.genes))
        ]
        super(EssentialityExperiment, self).validate(
            model=model, checks=checks + custom)

    def evaluate(self, model):
        """Use the defined parameters to predict single gene essentiality."""
        with model:
            if self.medium is not None:
                self.medium.apply(model)
            if self.objective is not None:
                model.objective = self.objective
            model.add_cons_vars(self.constraints)
            max_val = model.slim_optimize()
            essen = single_gene_deletion(
                model, gene_list=self.data["gene"], processes=1)
        essen.index = [list(g)[0] for g in essen.index]
        essen["essential"] = (essen["growth"] < (max_val * 0.1)) \
            | essen["growth"].isna()
        return essen
