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
Biomass tests performed on an instance of ``cobra.Model``.

N.B.: We parametrize each function here with the identified biomass reactions.
In the storage of test results we rely on the order of the biomass fixtures
to remain the same as the parametrized test cases.
"""

from __future__ import absolute_import

import os
import warnings

import pytest
import numpy as np
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    # ignore Gurobi warning
    from cobra.exceptions import Infeasible

import memote.support.biomass as biomass


BIOMASS_IDS = os.environ.get("BIOMASS_REACTIONS", "").split("|")


def test_biomass_presence(store):
    """Expect the model to contain at least one biomass reaction."""
    store["biomass_ids"] = BIOMASS_IDS
    assert len(BIOMASS_IDS) > 0, \
        "Could not identify any biomass reaction." \
        " Please change the intended reaction ID(s) to contain 'biomass'."


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
def test_biomass_consistency(read_only_model, reaction_id, store):
    """Expect biomass components to sum up to 1 g[CDW]."""
    store["biomass_sum"] = store.get("biomass_sum", list())
    reaction = read_only_model.reactions.get_by_id(reaction_id)
    component_sum = biomass.sum_biomass_weight(reaction)
    store["biomass_sum"].append(component_sum)
    assert np.isclose(component_sum, 1.0, atol=1e-03), \
        "{}'s components sum up to {} which is too far from " \
        "1 mmol / g[CDW] / h".format(reaction.id, component_sum)


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
def test_biomass_default_production(model, reaction_id, store):
    """Expect biomass production in default medium."""
    store["biomass_default_flux"] = store.get("biomass_default_flux", list())
    reaction = model.reactions.get_by_id(reaction_id)
    model.objective = reaction
    try:
        model.slim_optimize()
        flux = reaction.flux
    except Infeasible:
        flux = np.nan
    store["biomass_default_flux"].append(flux)
    assert flux > 0.0


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
def test_biomass_precursors_default_production(read_only_model, reaction_id,
                                               store):
    """Expect production of all biomass precursors in default medium."""
    store["default_blocked_precursors"] = store.get(
        "default_blocked_precursors", list())
    reaction = read_only_model.reactions.get_by_id(reaction_id)
    blocked = [
        met.id for met in biomass.find_blocked_biomass_precursors(
            reaction, read_only_model)]
    store["default_blocked_precursors"].append(blocked)
    assert len(blocked) == 0, \
        "{}'s following precursors cannot be produced: {}" \
        "".format(reaction.id, ", ".join(blocked))


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
def test_biomass_precursors_open_production(model, reaction_id, store):
    """Expect precursor production in complete medium."""
    store["open_blocked_precursors"] = store.get(
        "open_blocked_precursors", list())
    reaction = model.reactions.get_by_id(reaction_id)
    for exchange in model.exchanges:
        exchange.bounds = (-1000, 1000)
    blocked = [
        met.id for met in biomass.find_blocked_biomass_precursors(
            reaction, model)]
    store["open_blocked_precursors"].append(blocked)
    assert len(blocked) == 0, \
        "{}'s following precursors cannot be produced: {}" \
        "".format(reaction.id, ", ".join(blocked))


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
def test_gam_in_biomass(model, reaction_id, store):
    """Expect the biomass reactions to contain atp and adp."""
    store["gam_in_biomass"] = store.get(
        "gam_in_biomass", list())
    reaction = model.reactions.get_by_id(reaction_id)
    present = biomass.gam_in_biomass(reaction, model)
    store["gam_in_biomass"].append(present)
    assert present, \
        "{} does not contain a term for growth-associated maintenance." \
        "".format(reaction.id)


@pytest.mark.parametrize("reaction_id", BIOMASS_IDS)
def test_fast_growth_default(model, reaction_id):
    """Expect the predicted growth rate for each BOF to be below 10.3972.

    This is based on lowest doubling time reported here
    http://www.pnnl.gov/science/highlights/highlight.asp?id=879
    """
    reaction = model.reactions.get_by_id(reaction_id)
    model.objective = reaction
    try:
        model.slim_optimize()
        flux = reaction.flux
    except Infeasible:
        flux = np.nan
    assert flux <= 10.3972
