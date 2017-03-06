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

import memote.support.consistency as consistency


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
        rxn_3.add_metabolites({met_c: -1, met_c_prime: -1, met_a: 1})
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
        # Example in figure 3 of Gevorgyan et al. (2008) Bioinformatics
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
    ("fig-1", ["R1", "R2", "R3"]),
    ("eq-8", ["R1", "R2", "R3"]),
    ("fig-2", ["R2", "R4"]),
], indirect=["model"])
def test_find_inconsistent_min_stoichiometry(model, inconsistent):
    unconserved_rxns = consistency.find_inconsistent_min_stoichiometry(model)
    assert set([rxn.id for rxn in unconserved_rxns]) == set(inconsistent)
