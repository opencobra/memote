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


def figure_1(base):
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
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


def equation_8(base):
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
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


def figure_2(base):
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
    base.add_reactions([rxn_1, rxn_2, rxn_3, rxn_4])
    return base


def produces_atp(base):
    met_a = cobra.Metabolite("atp_c")
    met_b = cobra.Metabolite("A")
    met_c = cobra.Metabolite("B")
    rxn1 = cobra.Reaction("Gen")
    rxn1.add_metabolites({met_b: -1, met_a: 1, met_c: 1})
    rxn2 = cobra.Reaction("Recap", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_c: -1, met_b: 1})
    rxn3 = cobra.Reaction("EX_atp_c", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_a: -1})
    rxn4 = cobra.Reaction("EX_A_c", lower_bound=-1000, upper_bound=1000)
    rxn4.add_metabolites({met_b: -1})
    rxn5 = cobra.Reaction("EX_B_c", lower_bound=-1000, upper_bound=1000)
    rxn5.add_metabolites({met_c: -1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5])
    return base


def no_atp(base):
    met_a = cobra.Metabolite("atp_c")
    met_b = cobra.Metabolite("A")
    met_c = cobra.Metabolite("B")
    met_d = cobra.Metabolite("adp_c")
    rxn1 = cobra.Reaction("Gen")
    rxn1.add_metabolites({met_d: -1, met_b: -1, met_a: 1, met_c: 1})
    rxn2 = cobra.Reaction("Recap", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_c: -1, met_b: 1})
    rxn3 = cobra.Reaction("EX_atp_c", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_a: -1})
    rxn4 = cobra.Reaction("EX_A_c", lower_bound=-1000, upper_bound=1000)
    rxn4.add_metabolites({met_b: -1})
    rxn5 = cobra.Reaction("EX_B_c", lower_bound=-1000, upper_bound=1000)
    rxn5.add_metabolites({met_c: -1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5])
    return base


def all_balanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


def mass_imbalanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn1])
    return base


def charge_imbalanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=1)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


def loopy_toy_model(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABC"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["VA", "VB", "v1", "v2", "v3"]]
                       )
    base.reactions.VA.add_metabolites({"A": 1})
    base.reactions.VB.add_metabolites({"C": -1})
    base.reactions.v1.add_metabolites({"A": -1, "B": 1})
    base.reactions.v2.add_metabolites({"B": -1, "C": 1})
    base.reactions.v3.add_metabolites({"A": -1, "C": 1})
    base.reactions.v1.bounds = -1000, 1000
    base.reactions.v2.bounds = -1000, 1000
    base.reactions.v3.bounds = -1000, 1000
    base.objective = 'VB'
    base.reactions.VB.bounds = 0, 1
    return base


def constrained_toy_model(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABC"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["VA", "VB", "v1", "v2", "v3"]]
                       )
    base.reactions.VA.add_metabolites({"A": 1})
    base.reactions.VB.add_metabolites({"C": -1})
    base.reactions.v1.add_metabolites({"A": -1, "B": 1})
    base.reactions.v2.add_metabolites({"B": -1, "C": 1})
    base.reactions.v3.add_metabolites({"A": -1, "C": 1})
    base.reactions.v1.bounds = -1000, 1000
    base.reactions.v2.bounds = -1000, 1000
    base.reactions.v3.bounds = 1, 1
    base.objective = 'VB'
    base.reactions.VB.bounds = 0, 1
    return base


def model_builder(name):
    choices = {
        "fig-1": figure_1,
        "eq-8": equation_8,
        "fig-2": figure_2,
        "produces_atp": produces_atp,
        "no_atp": no_atp,
        "all_balanced": all_balanced,
        "mass_imbalanced": mass_imbalanced,
        "charge_imbalanced": charge_imbalanced,
        "loopy_toy_model": loopy_toy_model,
        "constrained_toy_model": constrained_toy_model,
    }
    model = cobra.Model(id_or_model=name, name=name)
    return choices[name](model)


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


@pytest.mark.parametrize("model, atp_production", [
    ("produces_atp", True),
    ("no_atp", False)
], indirect=["model"])
def test_production_of_atp_closed_bounds(model, atp_production):
    """Expect that ATP cannot be produced when all the bounds are closed."""
    production_of_atp = consistency.produce_atp_closed_exchanges(model)
    assert production_of_atp is atp_production


@pytest.mark.parametrize("model, num", [
    ("all_balanced", 0),
    ("mass_imbalanced", 1),
    ("charge_imbalanced", 1)
], indirect=["model"])
def test_imbalanced_reactions(model, num):
    """Expect all reactions to be mass and charge balanced."""
    reactions = consistency.find_imbalanced_reactions(model)
    assert len(reactions) == num


@pytest.mark.parametrize("model, num", [
    ("produces_atp", 0),
    ("no_atp", 2),
], indirect=["model"])
def test_blocked_reactions(model, num):
    """Expect all reactions to be able to carry flux."""
    dict_of_blocked_rxns = consistency.find_blocked_reactions(model)
    assert len(dict_of_blocked_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("loopy_toy_model", 3),
    ("constrained_toy_model", 0),
], indirect=["model"])
def test_find_stoichiometrically_balanced_cycles(model, num):
    """Expect no stoichiometrically balanced loops to be present."""
    rxns_in_loops = consistency.find_stoichiometrically_balanced_cycles(model)
    assert len(rxns_in_loops) == num
