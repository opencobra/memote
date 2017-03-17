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

import memote.support.consistency as consistency
import memote.support.helpers as helpers


def model_builder(name):
    model = cobra.Model(id_or_model=name, name=name)
    if name == "fig-1":
        # Example in figure 1 of Gevorgyan et al. (2008) Bioinformatics
        # Metabolites
        met_a = cobra.Metabolite("A")
        met_a_prime = cobra.Metabolite("A'")
        met_b = cobra.Metabolite("B")
        met_b_prime = cobra.Metabolite("B'")
        met_c = cobra.Metabolite("C")
        met_c_prime = cobra.Metabolite("C'")
        # Reactions
        rxn_1 = cobra.Reaction("R1")
        rxn_1.add_metabolites({met_a: -1, met_a_prime: -1, met_b: 1})
        rxn_2 = cobra.Reaction("R2")
        rxn_2.add_metabolites({met_b: -1, met_b_prime: -1, met_c: 1})
        rxn_3 = cobra.Reaction("R3")
        rxn_3.add_metabolites({met_c: -1, met_c_prime: -2, met_a: 1})
        model.add_reactions([rxn_1, rxn_2, rxn_3])
        return model
    if name == "eq-8":
        # Example in equation 8 of Gevorgyan et al. (2008) Bioinformatics
        # Metabolites
        met_a = cobra.Metabolite("A")
        met_b = cobra.Metabolite("B")
        met_c = cobra.Metabolite("C")
        # Reactions
        rxn_1 = cobra.Reaction("R1")
        rxn_1.add_metabolites({met_a: -1, met_b: 1, met_c: 1})
        rxn_2 = cobra.Reaction("R2")
        rxn_2.add_metabolites({met_a: -1, met_b: 1})
        rxn_3 = cobra.Reaction("R3")
        rxn_3.add_metabolites({met_a: -1, met_c: 1})
        model.add_reactions([rxn_1, rxn_2, rxn_3])
        return model
    if name == "fig-2":
        # Example in figure 2 of Gevorgyan et al. (2008) Bioinformatics
        # Metabolites
        met_a = cobra.Metabolite("A")
        met_b = cobra.Metabolite("B")
        met_x = cobra.Metabolite("X")
        met_p = cobra.Metabolite("P")
        met_q = cobra.Metabolite("Q")
        # Reactions
        rxn_1 = cobra.Reaction("R1")
        rxn_1.add_metabolites({met_a: -1, met_b: 1})
        rxn_2 = cobra.Reaction("R2")
        rxn_2.add_metabolites({met_a: -1, met_b: 1, met_x: 1})
        rxn_3 = cobra.Reaction("R3")
        rxn_3.add_metabolites({met_p: -1, met_q: 1})
        rxn_4 = cobra.Reaction("R4")
        rxn_4.add_metabolites({met_p: -1, met_q: 1, met_x: 1})
        model.add_reactions([rxn_1, rxn_2, rxn_3, rxn_4])
        return model

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


@pytest.mark.parametrize("model, consistent", [
    ("textbook", True),
    ("fig-1", False),
    ("eq-8", False),
    ("fig-2", False),
], indirect=["model"])
def test_check_stoichiometric_consistency(model, consistent):
    assert consistency.check_stoichiometric_consistency(model) is consistent


@pytest.mark.parametrize("model, inconsistent", [
    ("textbook", []),
    ("fig-1", ["A'", "B'", "C'"]),
    ("eq-8", ["A", "B", "C"]),
    ("fig-2", ["X"]),
], indirect=["model"])
def test_find_unconserved_metabolites(model, inconsistent):
    unconserved_mets = consistency.find_unconserved_metabolites(model)
    assert set([met.id for met in unconserved_mets]) == set(inconsistent)


@pytest.mark.parametrize("model, inconsistent", [
    ("textbook", []),
    ("fig-1", [("A'",), ("B'",), ("C'",)]),
    ("eq-8", [("A",), ("B",), ("C",)]),
    ("fig-2", [("X",)]),
], indirect=["model"])
def test_find_inconsistent_min_stoichiometry(model, inconsistent):
    unconserved_sets = consistency.find_inconsistent_min_stoichiometry(model)
    for unconserved in unconserved_sets:
        assert tuple(met.id for met in unconserved) in set(inconsistent)


@pytest.mark.parametrize("model, boolean", [
    ("sum_within_deviation", True),
    ("sum_outside_of_deviation", False),
], indirect=["model"])
def test_biomass_consistency(model, boolean):
    """
    Expect that the sum of total mass of all biomass components equals 1

    A deviation of 0.001 is considered as close enough.
    """
    biomass_rxns = helpers.find_biomass_reaction(model)
    for rxn in biomass_rxns:
        control_sum = consistency.calculate_sum_of_biomass_components(rxn)
        assert np.isclose([1], [control_sum], atol=1e-03)[0] == boolean
