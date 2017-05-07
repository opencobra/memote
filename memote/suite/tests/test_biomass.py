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

from builtins import zip

import pytest
import numpy as np
from cobra.exceptions import Infeasible

import memote.support.biomass as biomass
from memote.support.helpers import find_biomass_reaction


@pytest.fixture(scope="module")
def biomass_reactions(read_only_model):
    """Provide any biomass reactions found in the model."""
    return find_biomass_reaction(read_only_model)


def test_biomass_presence(biomass_reactions, store):
    """Expect the model to contain at least one biomass reaction."""
    store["biomass_reactions"] = [rxn.id for rxn in biomass_reactions]
    assert len(biomass_reactions) > 0, \
        "Could not identify any biomass reaction." \
        " Please change the intended reaction ID(s) to contain 'biomass'."


def test_biomass_consistency(biomass_reactions, store):
    """Expect biomass components to sum up to 1 g / mmol / h."""
    store["biomass_sum"] = [
        biomass.sum_biomass_weight(rxn) for rxn in biomass_reactions]
    for rxn, cntrl_sum in zip(store["biomass_reactions"], store["biomass_sum"]):
        assert np.isclose(cntrl_sum, 1.0, atol=1e-03), \
            "{}'s components sum up to {} which is too far from 1 g / mmol / h"\
            "".format(rxn, cntrl_sum)


def test_biomass_default_production(model, biomass_reactions, store):
    """Expect biomass production in default medium."""
    store["biomass_default_flux"] = list()
    for rxn in biomass_reactions:
        model.objective = rxn
        try:
            solution = model.optimize()
            store["biomass_default_flux"].append(solution.fluxes[rxn.id])
        except Infeasible:
            store["biomass_default_flux"].append(np.nan)
    for flux in store["biomass_default_flux"]:
        assert flux > 0.0


def test_biomass_precursors_default_production(model, biomass_reactions, store):
    """Expect production of all biomass precursors in default medium."""
    store["default_blocked_recursors"] = list()
    for rxn in biomass_reactions:
        store["default_blocked_recursors"].append(
            [met.id
             for met in biomass.find_blocked_biomass_precursors(rxn, model)])
    for rxn, blocked in zip(biomass_reactions,
                            store["default_blocked_recursors"]):
        assert len(blocked) == 0,\
            "{}'s following precursors cannot be produced: {}"\
            "".format(rxn.id, ", ".join(blocked))


def test_biomass_precursors_open_production(model, biomass_reactions, store):
    """Expect precursor production in complete medium."""
    store["open_blocked_precursors"] = list()
    for exchange in model.exchanges:
        exchange.bounds = (-1000, 1000)
    for rxn in biomass_reactions:
        store["open_blocked_precursors"].append(
            [met.id
             for met in biomass.find_blocked_biomass_precursors(rxn, model)])
    for rxn, blocked in zip(biomass_reactions,
                            store["open_blocked_precursors"]):
        assert len(blocked) == 0, \
            "{}'s following precursors cannot be produced: {}" \
            "".format(rxn.id, ", ".join(blocked))
