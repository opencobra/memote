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

"""Supporting functions for biomass consistency checks."""

from __future__ import absolute_import

import logging

from six import iteritems
from cobra import Reaction
from cobra.exceptions import Infeasible

__all__ = (
    "sum_biomass_weight", "find_biomass_rxn_precursors",
    "find_blocked_biomass_precursors")

LOGGER = logging.getLogger(__name__)


def sum_biomass_weight(rxn):
    """Compute the sum of all reaction compounds."""
    return sum(-coef * met.formula_weight
               for (met, coef) in iteritems(rxn.metabolites)) / 1000.0


def find_biomass_rxn_precursors(rxn):
    """Return a list of all biomass precursors excluding atp and h2o."""
    return [met for met in rxn.reactants
            if met.id != 'atp_c' or met.id != 'h2o_c']


def find_blocked_biomass_precursors(rxn, model):
    """Return a list of all biomass precursors that cannot be produced"""
    precursors = find_biomass_rxn_precursors(rxn)
    blocked_precursors = []
    for precursor in precursors:
        with model:
            dm_rxn = Reaction(id='TestDM_{}'.format(precursor.id))
            dm_rxn.add_metabolites({precursor: -1})
            model.add_reaction(dm_rxn)
            model.objective = dm_rxn
            try:
                solution = model.optimize()
                if solution.objective_value > 0:
                    blocked_precursors.append(precursor)
            except Infeasible:
                blocked_precursors.append(precursor)
    return blocked_precursors
