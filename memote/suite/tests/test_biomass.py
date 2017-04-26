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

"""Supporting functions for stoichiometric consistency checks."""

from __future__ import absolute_import

import numpy as np

import memote.support.biomass as biomass
from cobra.exceptions import Infeasible
import memote.support.helpers as helpers


def test_biomass_consistency(model):
    """
    Expect that the sum of total mass of all biomass components equals 1.

    Allow for an absolute tolerance of 1e-03.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        control_sum = biomass.sum_biomass_weight(rxn)
        assert np.isclose(1.0, control_sum, atol=1e-03), \
            "The following biomass reaction does not sum close enough to 1" \
            " {}".format(
            ", ".join(rxn.id))


def test_biomass_production(model):
    """
    Expect that biomass can be produced when optimizing the model.

    This is without changing the model's default state.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        model.objective = rxn
        try:
            solution = model.optimize()
            if solution.objective_value > 0:
                status = True
            else:
                status = False
        except Infeasible:
            status = False
        assert status is True


def test_production_biomass_precursors_default(model):
    """
    Expect that there are no biomass precursors that cannot be produced.

    This is without changing the model's default state.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        blocked_mets = biomass.find_blocked_biomass_precursors(rxn, model)
        assert len(blocked_mets) == 0, \
            "The biomass precursors of {} cannot be produced in the " \
            "default state of the model: {}".format(
            rxn, ", ".join([met.id for met in blocked_mets]))


def test_production_biomass_precursors_open(model):
    """
    Expect that there are no biomass precursors that cannot be produced.

    This is after opening all the model's exchange reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        with model:
            for exchange in model.exchanges:
                exchange.bounds = (-1000, 1000)
            blocked_mets = biomass.find_blocked_biomass_precursors(rxn, model)
            assert len(blocked_mets) == 0, \
                "The biomass precursors of {} cannot be produced in the " \
                "model despite all exchanges having been opened: {}".format(
                rxn, ", ".join([met.id for met in blocked_mets]))
