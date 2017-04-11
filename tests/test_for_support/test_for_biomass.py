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
Tests ensuring that the functions in `memote.support.basic` work as expected.
"""

from __future__ import absolute_import

import cobra
import pytest
import numpy as np

import memote.support.helpers as helpers
import memote.support.biomass as biomass


def model_builder(name):
    model = cobra.Model(id_or_model=name, name=name)
    if name == "sum_within_deviation":
        ''' Metabolites for a superficial, simple toy biomass reaction. The
        composition will follow the distribution depicted here:

        Lipid = 10% = 0.1 g/g
        Protein = 70% = 0.7 g/g
        RNA = 5% = 0.05 g/g
        DNA = 3% = 0.03 g/g
        Ash = 7% = 0.07 g/g
        Carbohydrates = 5% = 0.05 g/g

        The arbitrary molar masses for the metabolites used in this toy
        reaction will be approximated using hydrogen atoms in the formula.
        '''
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
        model.add_reactions([rxn_1])
        return model
    if name == "sum_outside_of_deviation":
        ''' Same as above, yet here H2O is on the wrong side of the equation
        which will throw off the balance.
        '''
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
        model.add_reactions([rxn_1])
        return model
    if name == "precursors_producing":
        met_a = cobra.Metabolite("lipid_c")
        met_b = cobra.Metabolite("protein_c")
        met_c = cobra.Metabolite("rna_c")
        met_a1 = cobra.Metabolite("lipid_e")
        met_b1 = cobra.Metabolite("protein_e")
        met_c1 = cobra.Metabolite("rna_e")
        # Reactions
        rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
        rxn.add_metabolites({met_a: -0.133, met_b: -5.834, met_c: -0.1})
        rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
        rxn1.add_metabolites({met_a: 1, met_a1: -1})
        rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
        rxn2.add_metabolites({met_b: 1, met_b1: -1})
        rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=1000)
        rxn3.add_metabolites({met_c: 1, met_c1: -1})
        rxn4 = cobra.Reaction("EX_met_a1", lower_bound=-1000, upper_bound=1000)
        rxn4.add_metabolites({met_a1: -1})
        rxn5 = cobra.Reaction("EX_met_b1", lower_bound=-1000, upper_bound=1000)
        rxn5.add_metabolites({met_b1: -1})
        rxn6 = cobra.Reaction("EX_met_c1", lower_bound=-1000, upper_bound=1000)
        rxn6.add_metabolites({met_c1: -1})
        model.add_reactions([rxn, rxn1, rxn2, rxn3, rxn4, rxn5, rxn6])
        return model
    if name == "precursors_blocked":
        met_a = cobra.Metabolite("lipid_c")
        met_b = cobra.Metabolite("protein_c")
        met_c = cobra.Metabolite("rna_c")
        met_a1 = cobra.Metabolite("lipid_e")
        met_b1 = cobra.Metabolite("protein_e")
        met_c1 = cobra.Metabolite("rna_e")
        # Reactions
        rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
        rxn.add_metabolites({met_a: -0.133, met_b: -5.834, met_c: -0.1})
        rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
        rxn1.add_metabolites({met_a: 1, met_a1: -1})
        rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
        rxn2.add_metabolites({met_b: 1, met_b1: -1})
        rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=0)
        rxn3.add_metabolites({met_c: 1, met_c1: -1})
        rxn4 = cobra.Reaction("EX_met_a1", lower_bound=-1000, upper_bound=1000)
        rxn4.add_metabolites({met_a1: -1})
        rxn5 = cobra.Reaction("EX_met_b1", lower_bound=-1000, upper_bound=1000)
        rxn5.add_metabolites({met_b1: -1})
        rxn6 = cobra.Reaction("EX_met_c1", lower_bound=-1000, upper_bound=1000)
        rxn6.add_metabolites({met_c1: -1})
        model.add_reactions([rxn, rxn1, rxn2, rxn3, rxn4, rxn5, rxn6])
        return model
    if name == "precursors_not_in_medium":
        met_a = cobra.Metabolite("lipid_c")
        met_b = cobra.Metabolite("protein_c")
        met_c = cobra.Metabolite("rna_c")
        met_a1 = cobra.Metabolite("lipid_e")
        met_b1 = cobra.Metabolite("protein_e")
        met_c1 = cobra.Metabolite("rna_e")
        # Reactions
        rxn = cobra.Reaction("BIOMASS_TEST", lower_bound=0, upper_bound=1000)
        rxn.add_metabolites({met_a: -0.133, met_b: -5.834, met_c: -0.1})
        rxn1 = cobra.Reaction("MET_Atec", lower_bound=-1000, upper_bound=1000)
        rxn1.add_metabolites({met_a: 1, met_a1: -1})
        rxn2 = cobra.Reaction("MET_Btec", lower_bound=-1000, upper_bound=1000)
        rxn2.add_metabolites({met_b: 1, met_b1: -1})
        rxn3 = cobra.Reaction("MET_Ctec", lower_bound=-1000, upper_bound=1000)
        rxn3.add_metabolites({met_c: 1, met_c1: -1})
        rxn4 = cobra.Reaction("EX_met_a1", lower_bound=0, upper_bound=1000)
        rxn4.add_metabolites({met_a1: -1})
        rxn5 = cobra.Reaction("EX_met_b1", lower_bound=0, upper_bound=1000)
        rxn5.add_metabolites({met_b1: -1})
        rxn6 = cobra.Reaction("EX_met_c1", lower_bound=-1000, upper_bound=1000)
        rxn6.add_metabolites({met_c1: -1})
        model.add_reactions([rxn, rxn1, rxn2, rxn3, rxn4, rxn5, rxn6])
        return model


@pytest.mark.parametrize("model, boolean", [
    ("sum_within_deviation", True),
    ("sum_outside_of_deviation", False),
], indirect=["model"])
def test_biomass_weight_production(model, boolean):
    """
    Expect that the sum of total mass of all biomass components equals 1.

    Allow for an absolute tolerance of 1e-03.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        control_sum = biomass.sum_biomass_weight(rxn)
        assert np.isclose(1, control_sum, atol=1e-03) is boolean


@pytest.mark.parametrize("model, num", [
    ("precursors_producing", 0),
    ("precursors_not_in_medium", 2),
    ("precursors_blocked", 1)
], indirect=["model"])
def test_production_biomass_precursors_dflt(model, num):
    """
    Expect that there are no biomass precursors that cannot be produced.

    This is without changing the model's default state.
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
def test_production_biomass_precursors_xchngs(model,num):
    """
    Expect that there are no biomass precursors that cannot be produced.

    This is after opening the model's exchange reactions.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        with model:
            xchngs = helpers.find_demand_and_exchange_reactions(model)
            for exchange in xchngs:
                exchange.bounds = [-1000, 1000]
            blocked_mets = biomass.find_blocked_biomass_precursors(rxn, model)
            assert len(blocked_mets) == num
