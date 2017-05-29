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

"""
Supporting functions for stoichiometric consistency checks.

N.B.: We parametrize each function here with the identified biomass reactions.
In the storage of test results we rely on the order of the biomass fixtures
to remain the same as the parametrized test cases.
"""

from __future__ import absolute_import

import pytest
import numpy as np
from cobra.exceptions import Infeasible

import memote.support.biomass as biomass
from memote.support.helpers import find_biomass_reaction


@pytest.fixture(scope="module")
def biomass_reactions(read_only_model):
    """Return any biomass reactions found in the model."""
    return find_biomass_reaction(read_only_model)


@pytest.fixture(scope="module")
def biomass_ids(biomass_reactions):
    """Return any biomass reaction IDs found in the model."""
    return [rxn.id for rxn in biomass_reactions]


def test_biomass_presence(biomass_ids, store):
    """Expect the model to contain at least one biomass reaction."""
    store["biomass_ids"] = biomass_ids
    assert len(biomass_ids) > 0, \
        "Could not identify any biomass reaction." \
        " Please change the intended reaction ID(s) to contain 'biomass'."


@pytest.mark.parametrize("reaction", biomass_reactions, ids=biomass_ids)
def test_biomass_consistency(reaction, store):
    """Expect biomass components to sum up to 1 g / mmol / h."""
    store["biomass_sum"] = store.get("biomass_sum", list())
    component_sum = biomass.sum_biomass_weight(reaction)
    store["biomass_sum"].append(component_sum)
    assert np.isclose(component_sum, 1.0, atol=1e-03), \
        "{}'s components sum up to {} which is too far from 1 mmol / g / h"\
        "".format(reaction.id, component_sum)


@pytest.mark.parametrize("reaction", biomass_reactions, ids=biomass_ids)
def test_biomass_default_production(model, reaction, store):
    """Expect biomass production in default medium."""
    store["biomass_default_flux"] = store.get("biomass_default_flux", list())
    model.objective = reaction
    try:
        solution = model.optimize()
        flux = solution.fluxes[reaction.id]
    except Infeasible:
        flux = np.nan
    store["biomass_default_flux"].append(flux)
    assert flux > 0.0


@pytest.mark.parametrize("reaction", biomass_reactions, ids=biomass_ids)
def test_biomass_precursors_default_production(read_only_model, reaction,
                                               store):
    """Expect production of all biomass precursors in default medium."""
    store["default_blocked_precursors"] = store.get(
        "default_blocked_precursors", list())
    blocked = [
        met.id for met in biomass.find_blocked_biomass_precursors(
            reaction, read_only_model)]
    store["default_blocked_precursors"].append(blocked)
    assert len(blocked) == 0, \
        "{}'s following precursors cannot be produced: {}" \
        "".format(reaction.id, ", ".join(blocked))


@pytest.mark.parametrize("reaction", biomass_reactions, ids=biomass_ids)
def test_biomass_precursors_open_production(model, reaction, store):
    """Expect precursor production in complete medium."""
    store["open_blocked_precursors"] = store.get(
        "open_blocked_precursors", list())
    for exchange in model.exchanges:
        exchange.bounds = (-1000, 1000)
    blocked = [
        met.id for met in biomass.find_blocked_biomass_precursors(
            reaction, model)]
    store["open_blocked_precursors"].append(blocked)
    assert len(blocked) == 0, \
        "{}'s following precursors cannot be produced: {}" \
        "".format(reaction.id, ", ".join(blocked))
