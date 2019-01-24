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

"""Ensure the expected functioning of ``memote.support.matrix``."""

from __future__ import absolute_import

import pytest
from cobra import Metabolite, Reaction

import memote.support.matrix as matrix
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def three_components_closed(base):
    """Returns a simple model with 3 metabolites in a closed system."""
    met_a = Metabolite("A")
    met_b = Metabolite("B")
    met_c = Metabolite("C")
    rxn_1 = Reaction("R1", lower_bound=-1000, upper_bound=1000)
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    rxn_2 = Reaction("R2", lower_bound=-1000, upper_bound=1000)
    rxn_2.add_metabolites({met_b: -1, met_c: 1})
    base.add_reactions([rxn_1, rxn_2])
    return base


@register_with(MODEL_REGISTRY)
def three_components_open(base):
    """Returns a simple model with 3 metabolites in an open system."""
    met_a = Metabolite("A")
    met_b = Metabolite("B")
    met_c = Metabolite("C")
    rxn_1 = Reaction("R1", lower_bound=-1000, upper_bound=1000)
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    rxn_2 = Reaction("R2", lower_bound=-1000, upper_bound=1000)
    rxn_2.add_metabolites({met_b: -1, met_c: 1})
    rxn_b1 = Reaction("B1", lower_bound=0, upper_bound=1000)
    rxn_b1.add_metabolites({met_a: 1})
    rxn_b2 = Reaction("B2", lower_bound=0, upper_bound=1000)
    rxn_b2.add_metabolites({met_c: -1})
    base.add_reactions([rxn_1, rxn_2, rxn_b1, rxn_b2])
    return base


@register_with(MODEL_REGISTRY)
def x2_cycle_closed(base):
    x1 = Metabolite("x1")
    x2 = Metabolite("x2")
    x3 = Metabolite("x3")
    x4 = Metabolite("x4")
    x5 = Metabolite("x5")
    rxn_1 = Reaction("R1", lower_bound=-1000, upper_bound=1000)
    rxn_1.add_metabolites({x1: -1, x2: -1, x3: 1})
    rxn_2 = Reaction("R2", lower_bound=-1000, upper_bound=1000)
    rxn_2.add_metabolites({x3: -1, x4: 1})
    rxn_3 = Reaction("R3", lower_bound=-1000, upper_bound=1000)
    rxn_3.add_metabolites({x4: -1, x5: 1, x2: 1})
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


@register_with(MODEL_REGISTRY)
def x2_cycle_open(base):
    x1 = Metabolite("x1")
    x2 = Metabolite("x2")
    x3 = Metabolite("x3")
    x4 = Metabolite("x4")
    x5 = Metabolite("x5")
    rxn_1 = Reaction("R1", lower_bound=-1000, upper_bound=1000)
    rxn_1.add_metabolites({x1: -1, x2: -1, x3: 1})
    rxn_2 = Reaction("R2", lower_bound=-1000, upper_bound=1000)
    rxn_2.add_metabolites({x3: -1, x4: 1})
    rxn_3 = Reaction("R3", lower_bound=-1000, upper_bound=1000)
    rxn_3.add_metabolites({x4: -1, x5: 1, x2: 1})
    rxn_b1 = Reaction("B1", lower_bound=0, upper_bound=1000)
    rxn_b1.add_metabolites({x1: 1})
    rxn_b2 = Reaction("B2", lower_bound=0, upper_bound=1000)
    rxn_b2.add_metabolites({x5: -1})
    base.add_reactions([rxn_1, rxn_2, rxn_3, rxn_b1, rxn_b2])
    return base


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", (1, 1)),
    ("three_components_open", (1, 1)),
    ("x2_cycle_closed", (1, 1)),
    ("x2_cycle_open", (1, 1)),
], indirect=["model"])
def test_absolute_extreme_coefficient_ratio(model, num):
    assert matrix.absolute_extreme_coefficient_ratio(model) == num


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", 1),
    ("three_components_open", 0),
    ("x2_cycle_closed", 2),
    ("x2_cycle_open", 1),
], indirect=["model"])
def test_number_independent_conservation_relations(model, num):
    assert matrix.number_independent_conservation_relations(model) == num


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", 2),
    ("three_components_open", 3),
    ("x2_cycle_closed", 3),
    ("x2_cycle_open", 4),
], indirect=["model"])
def test_matrix_rank(model, num):
    assert matrix.matrix_rank(model) == num


@pytest.mark.parametrize("model, num", [
    ("three_components_closed", 0),
    ("three_components_open", 1),
    ("x2_cycle_closed", 0),
    ("x2_cycle_open", 1),
], indirect=["model"])
def test_degrees_of_freedom(model, num):
    assert matrix.degrees_of_freedom(model) == num
