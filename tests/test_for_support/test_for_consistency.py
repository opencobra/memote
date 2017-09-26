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


def free_reactions(base):
    met_a = cobra.Metabolite("C")
    met_b = cobra.Metabolite("A")
    met_c = cobra.Metabolite("B")
    rxn1 = cobra.Reaction("Gen")
    rxn1.add_metabolites({met_b: -1, met_a: 1, met_c: 1})
    rxn2 = cobra.Reaction("Recap", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_c: -1, met_b: 1})
    rxn3 = cobra.Reaction("EX_C_c", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_a: -1})
    rxn4 = cobra.Reaction("EX_A_c", lower_bound=-1000, upper_bound=1000)
    rxn4.add_metabolites({met_b: -1})
    rxn5 = cobra.Reaction("EX_B_c", lower_bound=-1000, upper_bound=1000)
    rxn5.add_metabolites({met_c: -1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5])
    return base


def blocked_reactions(base):
    met_a = cobra.Metabolite("C")
    met_b = cobra.Metabolite("A")
    met_c = cobra.Metabolite("B")
    met_d = cobra.Metabolite("D")
    rxn1 = cobra.Reaction("Gen")
    rxn1.add_metabolites({met_d: -1, met_b: -1, met_a: 1, met_c: 1})
    rxn2 = cobra.Reaction("Recap", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_c: -1, met_b: 1})
    rxn3 = cobra.Reaction("EX_C_c", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_a: -1})
    rxn4 = cobra.Reaction("EX_A_c", lower_bound=-1000, upper_bound=1000)
    rxn4.add_metabolites({met_b: -1})
    rxn5 = cobra.Reaction("EX_B_c", lower_bound=-1000, upper_bound=1000)
    rxn5.add_metabolites({met_c: -1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5])
    return base


def produces_atp(base):
    """Returns a simple model with an EGC producing atp_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "atp_c + h2o_c + a <--> pi_c + adp_c + c + h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h2o_c, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.adp_c, type="sink")
    base.add_boundary(base.metabolites.atp_c, type="sink")
    base.add_boundary(base.metabolites.pi_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def infeasible(base):
    """Returns an infeasible model with an EGC producing atp_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    rd = cobra.Reaction('MAINTENANCE')
    base.add_reactions([ra, rb, rc, rd])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "atp_c + h2o_c + a <--> pi_c + adp_c + c + h_c"
    rd.reaction = "h2o_c + b --> c + h_c + met_c"
    rd.bounds = 10, 1000
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h2o_c, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.adp_c, type="sink")
    base.add_boundary(base.metabolites.atp_c, type="sink")
    base.add_boundary(base.metabolites.pi_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def maintenance_present(base):
    """Returns a model with an ATPM reaction"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    rd = cobra.Reaction('ATPM')
    base.add_reactions([ra, rb, rc, rd])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "atp_c + h2o_c + a <--> pi_c + adp_c + c + h_c"
    rd.reaction = "atp_c + h2o_c + a --> pi_c + adp_c + c + h_c"
    rd.bounds = 7.9, 1000
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h2o_c, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.adp_c, type="sink")
    base.add_boundary(base.metabolites.atp_c, type="sink")
    base.add_boundary(base.metabolites.pi_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def missing_energy_partner(base):
    """Returns a broken model with a missing energy partner to atp"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "atp_c + a <--> c "
    return base


def produces_nadh(base):
    """Returns a simple model with an EGC producing nadh_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "nadh_c + a <--> nad_c + c + h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.nad_c, type="sink")
    base.add_boundary(base.metabolites.nadh_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def produces_fadh2(base):
    """Returns a simple model with an EGC producing fadh2_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "fadh2_c + a <--> fad_c + c + 2 h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.fad_c, type="sink")
    base.add_boundary(base.metabolites.fadh2_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def produces_accoa(base):
    """Returns a simple model with an EGC producing accoa_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "accoa_c + h2o_c + a <--> coa_c + c + ac_c + h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.ac_c, type="sink")
    base.add_boundary(base.metabolites.h2o_c, type="sink")
    base.add_boundary(base.metabolites.coa_c, type="sink")
    base.add_boundary(base.metabolites.accoa_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def produces_glu(base):
    """Returns a simple model with an EGC producing glu__L_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "glu__L_c + h2o_c + a <--> c + akg_c + nh3_c + 2 h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.nh3_c, type="sink")
    base.add_boundary(base.metabolites.h2o_c, type="sink")
    base.add_boundary(base.metabolites.akg_c, type="sink")
    base.add_boundary(base.metabolites.glu__L_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def produces_h(base):
    """Returns a simple model with an EGC producing h_p"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "h_p + a <--> c + h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h_p, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def no_atp(base):
    """Returns a simple model without an EGC producing atp_c"""
    ra = cobra.Reaction('A')
    rb = cobra.Reaction('B')
    rc = cobra.Reaction('C')
    base.add_reactions([ra, rb, rc])
    ra.reaction = "a <--> b"
    rb.reaction = "b <--> c"
    rc.reaction = "atp_c + h2o_c + a --> pi_c + adp_c + c + h_c"
    base.add_boundary(base.metabolites.a, type="sink")
    base.add_boundary(base.metabolites.h2o_c, type="sink")
    base.add_boundary(base.metabolites.h_c, type="sink")
    base.add_boundary(base.metabolites.adp_c, type="sink")
    base.add_boundary(base.metabolites.atp_c, type="sink")
    base.add_boundary(base.metabolites.pi_c, type="sink")
    base.add_boundary(base.metabolites.c, type="demand")
    return base


def all_balanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


def mass_imbalanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=2)
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


def met_no_formula(base):
    met_a = cobra.Metabolite("A", formula=None, charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


def met_no_charge(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2')
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


def infeasible_toy_model(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABC"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["VA", "VB", "v1", "v2", "v3"]]
                       )
    base.reactions.VA.add_metabolites({"A": 1})
    base.reactions.VB.add_metabolites({"C": -1})
    base.reactions.v1.add_metabolites({"A": -1, "B": 1})
    base.reactions.v2.add_metabolites({"B": -1, "C": 1})
    base.reactions.v3.add_metabolites({"A": -1, "C": 1})
    # Forcing a lower bound on a 'metabolic' reaction that is higher than the
    # uptake rate will make a model infeasible.
    base.reactions.v1.bounds = 2, 1000
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
        "free_reactions": free_reactions,
        "blocked_reactions": blocked_reactions,
        "produces_atp": produces_atp,
        "no_atp": no_atp,
        "all_balanced": all_balanced,
        "mass_imbalanced": mass_imbalanced,
        "charge_imbalanced": charge_imbalanced,
        "met_no_charge": met_no_charge,
        "met_no_formula": met_no_formula,
        "loopy_toy_model": loopy_toy_model,
        "constrained_toy_model": constrained_toy_model,
        "infeasible_toy_model": infeasible_toy_model,
        "produces_accoa": produces_accoa,
        "produces_fadh2": produces_fadh2,
        "produces_glu": produces_glu,
        "produces_h": produces_h,
        "produces_nadh": produces_nadh,
        "missing_energy_partner": missing_energy_partner,
        "maintenance_present": maintenance_present,
        "infeasible": infeasible
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


@pytest.mark.parametrize("model, metabolite_id", [
    # test control flow statements
    ("produces_atp", 'atp_c'),
    ("produces_accoa", 'accoa_c'),
    ("produces_fadh2", "fadh2_c"),
    ("produces_glu", "glu__L_c"),
    ("produces_h", "h_p"),
    ("produces_nadh", "nadh_c"),
    ("maintenance_present", "atp_c"),
], indirect=["model"])
def test_detect_energy_generating_cycles_control_flow(model, metabolite_id):
    """Expect that energy-generating cycles don't exist for metabolite ID."""
    cycle = consistency.detect_energy_generating_cycles(model, metabolite_id)
    assert set(cycle) == {'A', 'B', 'C'}


@pytest.mark.parametrize("model, metabolite_id, output", [
    # test for possible exceptions
    pytest.mark.raises(("produces_nadh", "atp_c", None), exception=KeyError),
    pytest.mark.raises(("missing_energy_partner", "atp_c", None),
                       exception=KeyError),
    ("no_atp", "atp_c", []),
    ("infeasible", "atp_c", "infeasible")
], indirect=["model"])
def test_detect_energy_generating_cycles_exceptions(model, metabolite_id,
                                                    output):
    """Expect that energy-generating cycles don't exist for metabolite ID."""
    result = consistency.detect_energy_generating_cycles(model, metabolite_id)
    assert set(result) == set(output)


@pytest.mark.parametrize("model, num", [
    ("all_balanced", 0),
    ("mass_imbalanced", 0),
    ("charge_imbalanced", 1),
    ("met_no_charge", 1),
    ("met_no_formula", 0)
], indirect=["model"])
def test_find_charge_imbalanced_reactions(model, num):
    """Expect all reactions to be charge balanced."""
    reactions = consistency.find_charge_imbalanced_reactions(model)
    assert len(reactions) == num


@pytest.mark.parametrize("model, num", [
    ("all_balanced", 0),
    ("mass_imbalanced", 1),
    ("charge_imbalanced", 0),
    ("met_no_charge", 0),
    ("met_no_formula", 1)
], indirect=["model"])
def test_find_mass_imbalanced_reactions(model, num):
    """Expect all reactions to be mass balanced."""
    reactions = consistency.find_mass_imbalanced_reactions(model)
    assert len(reactions) == num


@pytest.mark.parametrize("model, num", [
    ("free_reactions", 0),
    ("blocked_reactions", 2),
], indirect=["model"])
def test_blocked_reactions(model, num):
    """Expect all reactions to be able to carry flux."""
    dict_of_blocked_rxns = consistency.find_blocked_reactions(model)
    assert len(dict_of_blocked_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("loopy_toy_model", 3),
    ("constrained_toy_model", 0),
    ("infeasible_toy_model", 0),
], indirect=["model"])
def test_find_stoichiometrically_balanced_cycles(model, num):
    """Expect no stoichiometrically balanced loops to be present."""
    rxns_in_loops = consistency.find_stoichiometrically_balanced_cycles(
        model
    )
    assert len(rxns_in_loops) == num
