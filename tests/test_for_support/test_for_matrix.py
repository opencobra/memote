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

"""Ensure the expected functioning of ``memote.support.consistency``."""

from __future__ import absolute_import

import cobra
import pytest
from cobra.exceptions import Infeasible

import memote.support.consistency as consistency
import memote.support.matrix as matrix
from memote.utils import register_with
import memote.support.consistency_helpers as con_helpers

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def three_components_closed(base):
    """Returns a simple model with 3 metabolites in a closed system."""
    met_a = cobra.Metabolite("A")
    met_b = cobra.Metabolite("B")
    met_c = cobra.Metabolite("C")
    rxn_1 = cobra.Reaction("R1", lower_bound=-1000, upper_bound=1000)
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    rxn_2 = cobra.Reaction("R2", lower_bound=-1000, upper_bound=1000)
    rxn_2.add_metabolites({met_b: -1, met_c: 1})
    base.add_reactions([rxn_1, rxn_2])
    return base


@register_with(MODEL_REGISTRY)
def four_components_closed(base):
    """Returns a simple model with 4 metabolites in a closed system."""
    met_a = cobra.Metabolite("A")
    met_b = cobra.Metabolite("B")
    met_c = cobra.Metabolite("C")
    met_d = cobra.Metabolite("D")
    rxn_1 = cobra.Reaction("R1", lower_bound=-1000, upper_bound=1000)
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    rxn_2 = cobra.Reaction("R2", lower_bound=-1000, upper_bound=1000)
    rxn_2.add_metabolites({met_b: -1, met_c: 1})
    rxn_3 = cobra.Reaction("R3", lower_bound=0, upper_bound=1000)
    rxn_3.add_metabolites({met_c: -1, met_d: 1})
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", 1),
], indirect=["model"])
def test_number_independent_conservation_relations(model, num):
    assert matrix.number_independent_conservation_relations(model) == num


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", 0),
], indirect=["model"])
def test_number_steady_state_flux_solutions(model, num):
    assert matrix.number_steady_state_flux_solutions(model) == num


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", 2),
], indirect=["model"])
def test_matrix_rank(model, num):
    assert matrix.matrix_rank(model) == num
