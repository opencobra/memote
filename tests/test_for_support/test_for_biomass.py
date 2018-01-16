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

"""Ensure the expected functioning of ``memote.support.biomass``."""

from __future__ import absolute_import

import cobra
import pytest
import numpy as np
from optlang.interface import OPTIMAL

import memote.support.helpers as helpers
import memote.support.biomass as biomass
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def sum_within_deviation(base):
    """Metabolites for a superficial, simple toy biomass reaction. The
    composition will follow the distribution depicted here:

    Lipid = 10% = 0.1 g/g
    Protein = 70% = 0.7 g/g
    RNA = 5% = 0.05 g/g
    DNA = 3% = 0.03 g/g
    Ash = 7% = 0.07 g/g
    Carbohydrates = 5% = 0.05 g/g

    The arbitrary molar masses for the metabolites used in this toy
    reaction will be approximated using hydrogen atoms in the formula.
    """
    met_a = cobra.Metabolite("lipid_c", "H744")
    met_b = cobra.Metabolite("protein_c", "H119")
    met_c = cobra.Metabolite("rna_c", "H496")
    met_d = cobra.Metabolite("dna_c", "H483")
    met_e = cobra.Metabolite("ash_c", "H80")
    met_f = cobra.Metabolite("cellwall_c", "H177")
    met_g = cobra.Metabolite("atp_c", "C10H12N5O13P3")
    met_h = cobra.Metabolite("adp_c", "C10H12N5O10P2")
    met_i = cobra.Metabolite("h_c", "H")
    met_j = cobra.Metabolite("h2o_c", "H2O")
    met_k = cobra.Metabolite("pi_c", "HO4P")
    # Reactions
    rxn_1 = cobra.Reaction("BIOMASS_TEST")
    rxn_1.add_metabolites({met_a: -0.133, met_b: -5.834, met_c: -0.1,
                           met_d: -0.0625, met_e: -0.875, met_f: -0.2778,
                           met_g: -30.0, met_h: 30.0, met_i: 30.0,
                           met_j: -30.0, met_k: 30.0
                           })
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def sum_outside_of_deviation(base):
    """ Same as above, yet here H2O is on the wrong side of the equation
    which will throw off the balance.
    """
    met_a = cobra.Metabolite("lipid_c", "H744")
    met_b = cobra.Metabolite("protein_c", "H119")
    met_c = cobra.Metabolite("rna_c", "H496")
    met_d = cobra.Metabolite("dna_c", "H483")
    met_e = cobra.Metabolite("ash_c", "H80")
    met_f = cobra.Metabolite("cellwall_c", "H177")
    met_g = cobra.Metabolite("atp_c", "C10H12N5O13P3")
    met_h = cobra.Metabolite("adp_c", "C10H12N5O10P2")
    met_i = cobra.Metabolite("h_c", "H")
    met_j = cobra.Metabolite("h2o_c", "H2O")
    met_k = cobra.Metabolite("pi_c", "HO4P")
    # Reactions
    rxn_1 = cobra.Reaction("BIOMASS_TEST")
    rxn_1.add_metabolites({met_a: -0.133, met_b: -5.834, met_c: -0.1,
                           met_d: -0.0625, met_e: -0.875, met_f: -0.2778,
                           met_g: -30.0, met_h: 30.0, met_i: 30.0,
                           met_j: 30.0, met_k: 30.0
                           })
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def precursors_producing(base):
    met_a = cobra.Metabolite("lipid_c")
    met_b = cobra.Metabolite("protein_c")
    met_c = cobra.Metabolite("rna_c")
    met_a1 = cobra.Metabolite("lipid_e")
    met_b1 = cobra.Metabolite("protein_e")
    met_c1 = cobra.Metabolite("rna_e")
    # Reactions
    rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
    rxn.add_metabolites({met_a: -1, met_b: -5, met_c: -2})
    rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
    rxn1.add_metabolites({met_a: 1, met_a1: -1})
    rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_b: 1, met_b1: -1})
    rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_c: 1, met_c1: -1})
    base.add_reactions([rxn, rxn1, rxn2, rxn3])
    base.add_boundary(met_a1)
    base.add_boundary(met_b1)
    base.add_boundary(met_c1)
    base.objective = rxn
    return base


@register_with(MODEL_REGISTRY)
def precursors_uptake_limited(base):
    met_a = cobra.Metabolite("lipid_c")
    met_b = cobra.Metabolite("protein_c")
    met_c = cobra.Metabolite("rna_c")
    met_a1 = cobra.Metabolite("lipid_e")
    met_b1 = cobra.Metabolite("protein_e")
    met_c1 = cobra.Metabolite("rna_e")
    # Reactions
    rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
    rxn.add_metabolites({met_a: -1, met_b: -5, met_c: -2})
    rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
    rxn1.add_metabolites({met_a: 1, met_a1: -1})
    rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_b: 1, met_b1: -1})
    rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_c: 1, met_c1: -1})
    base.add_reactions([rxn, rxn1, rxn2, rxn3])
    base.add_boundary(met_a1, ub=5)
    base.add_boundary(met_b1)
    base.add_boundary(met_c1)
    base.objective = rxn
    return base


@register_with(MODEL_REGISTRY)
def precursors_blocked(base):
    met_a = cobra.Metabolite("lipid_c")
    met_b = cobra.Metabolite("protein_c")
    met_c = cobra.Metabolite("rna_c")
    met_a1 = cobra.Metabolite("lipid_e")
    met_b1 = cobra.Metabolite("protein_e")
    met_c1 = cobra.Metabolite("rna_e")
    # Reactions
    rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
    rxn.add_metabolites({met_a: -1, met_b: -5, met_c: -2})
    rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
    rxn1.add_metabolites({met_a: 1, met_a1: -1})
    rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_b: 1, met_b1: -1})
    rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=0)
    rxn3.add_metabolites({met_c: 1, met_c1: -1})
    base.add_reactions([rxn, rxn1, rxn2, rxn3])
    base.add_boundary(met_a1)
    base.add_boundary(met_b1)
    base.add_boundary(met_c1)
    base.objective = rxn
    return base


@register_with(MODEL_REGISTRY)
def precursors_not_in_medium(base):
    met_a = cobra.Metabolite("lipid_c")
    met_b = cobra.Metabolite("protein_c")
    met_c = cobra.Metabolite("rna_c")
    met_a1 = cobra.Metabolite("lipid_e")
    met_b1 = cobra.Metabolite("protein_e")
    met_c1 = cobra.Metabolite("rna_e")
    # Reactions
    rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
    rxn.add_metabolites({met_a: -1, met_b: -5, met_c: -2})
    rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
    rxn1.add_metabolites({met_a: 1, met_a1: -1})
    rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_b: 1, met_b1: -1})
    rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_c: 1, met_c1: -1})
    base.add_reactions([rxn, rxn1, rxn2, rxn3])
    base.add_boundary(met_a1, ub=0)
    base.add_boundary(met_b1, ub=0)
    base.add_boundary(met_c1)
    base.objective = rxn
    return base


@register_with(MODEL_REGISTRY)
def no_gam_in_biomass(base):
    met_a = cobra.Metabolite("lipid_c", "H744")
    met_b = cobra.Metabolite("protein_c", "H119")
    met_c = cobra.Metabolite("rna_c", "H496")
    met_d = cobra.Metabolite("dna_c", "H483")
    met_e = cobra.Metabolite("ash_c", "H80")
    met_f = cobra.Metabolite("cellwall_c", "H177")
    met_g = cobra.Metabolite("atp_c", "C10H12N5O13P3")
    # Reactions
    rxn_1 = cobra.Reaction("BIOMASS_TEST")
    rxn_1.add_metabolites({met_a: -0.133, met_b: -5.834, met_c: -0.1,
                           met_d: -0.0625, met_e: -0.875, met_f: -0.2778,
                           met_g: -0.032})
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def direct_met_no_compartments(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABCDEFG"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["EX_A", "EX_C",
                                  "EX_E", "EX_G",
                                  "A2B", "C2D",
                                  "E2F", "biomass"]]
                       )
    base.reactions.EX_A.add_metabolites({"A": 1})
    base.reactions.EX_C.add_metabolites({"C": -1})
    base.reactions.EX_E.add_metabolites({"E": -1})
    base.reactions.EX_G.add_metabolites({"G": -1})
    base.reactions.A2B.add_metabolites({"A": -1, "B": 1})
    base.reactions.C2D.add_metabolites({"C": -1, "D": 1})
    base.reactions.E2F.add_metabolites({"E": -1, "F": 1})
    base.reactions.biomass.add_metabolites(
        {"B": -1, "D": -1, "F": -1, "G": -1}
    )
    return base


@pytest.mark.parametrize("model, expected", [
    ("sum_within_deviation", True),
    ("sum_outside_of_deviation", False),
], indirect=["model"])
def test_biomass_weight_production(model, expected):
    """
    Expect that the sum of total mass of all biomass components equals 1.

    Allow for an absolute tolerance of 1e-03.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        control_sum = biomass.sum_biomass_weight(rxn)
        assert np.isclose(1, control_sum, atol=1e-03) == expected


@pytest.mark.parametrize("model, expected", [
    ("precursors_producing", 200.0),
    ("precursors_not_in_medium", 0.0)
], indirect=["model"])
def test_biomass_production(model, expected):
    """
    Expect that biomass can be produced when optimizing the model.

    This is without changing the model"s default state.
    """
    solution = model.optimize()
    assert solution.status == OPTIMAL
    assert solution.objective_value == expected


@pytest.mark.parametrize("model, num", [
    ("precursors_producing", 0),
    ("precursors_not_in_medium", 2),
    ("precursors_blocked", 1)
], indirect=["model"])
def test_production_biomass_precursors_default(model, num):
    """
    Expect that there are no biomass precursors that cannot be produced.

    This is without changing the model"s default state.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        blocked_mets = biomass.find_blocked_biomass_precursors(rxn, model)
        assert len(blocked_mets) == num


@pytest.mark.parametrize("model, num", [
    ("precursors_producing", 0),
    ("precursors_not_in_medium", 0),
    ("precursors_blocked", 1)
], indirect=["model"])
def test_production_biomass_precursors_exchange(model, num):
    """
    Expect that there are no biomass precursors that cannot be produced.

    This is after opening the model"s exchange reactions.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        for exchange in model.exchanges:
            exchange.bounds = (-1000, 1000)
        blocked_mets = biomass.find_blocked_biomass_precursors(rxn, model)
        assert len(blocked_mets) == num


@pytest.mark.parametrize("model, boolean", [
    ("sum_within_deviation", True),
    ("no_gam_in_biomass", False)
], indirect=["model"])
def test_gam_in_biomass(model, boolean):
    """Expect the biomass reactions to contain atp and adp."""
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        assert biomass.gam_in_biomass(rxn) is boolean


@pytest.mark.parametrize("model, boolean", [
    ("precursors_producing", False),
    ("precursors_not_in_medium", True),
    ("precursors_uptake_limited", True)
], indirect=["model"])
def test_fast_growth_default(model, boolean):
    """
    Expect the predicted growth rate for each BOF to be below 10.3972.

    This is without changing the model"s default state.
    """
    solution = model.optimize()
    assert solution.status == OPTIMAL
    fast_growth = solution.objective_value <= 10.3972
    assert fast_growth == boolean


@pytest.mark.parametrize("model, number", [
    ("direct_met_no_compartments", 1),
    ("precursors_producing", 0)
], indirect=["model"])
def test_find_direct_metabolites(model, number):
    """Expect the appropriate amount of direct metabolites to be found."""
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        assert len(biomass.find_direct_metabolites(model, rxn)) is number
