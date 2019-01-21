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
from memote.utils import register_with
import memote.support.consistency_helpers as con_helpers

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
def blocked_reactions(base):
    met_a = cobra.Metabolite("C", compartment="e")
    met_b = cobra.Metabolite("A", compartment="e")
    met_c = cobra.Metabolite("B", compartment="e")
    met_d = cobra.Metabolite("D", compartment="e")
    rxn1 = cobra.Reaction("Gen")
    rxn1.add_metabolites({met_d: -1, met_b: -1, met_a: 1, met_c: 1})
    rxn2 = cobra.Reaction("Recap", lower_bound=-1000, upper_bound=1000)
    rxn2.add_metabolites({met_c: -1, met_b: 1})
    rxn3 = cobra.Reaction("EX_C_e", lower_bound=-1000, upper_bound=1000)
    rxn3.add_metabolites({met_a: -1})
    rxn4 = cobra.Reaction("EX_A_e", lower_bound=-1000, upper_bound=1000)
    rxn4.add_metabolites({met_b: -1})
    rxn5 = cobra.Reaction("EX_B_e", lower_bound=-1000, upper_bound=1000)
    rxn5.add_metabolites({met_c: -1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5])
    return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


# TODO: Removed until detection of organism type is implemented.
# @register_with(MODEL_REGISTRY)
# def produces_h(base):
#     """Returns a simple model with an EGC producing h_p"""
#     ra = cobra.Reaction('A')
#     rb = cobra.Reaction('B')
#     rc = cobra.Reaction('C')
#     base.add_reactions([ra, rb, rc])
#     ra.reaction = "a <--> b"
#     rb.reaction = "b <--> c"
#     rc.reaction = "h_p + a <--> c + h_c"
#     base.add_boundary(base.metabolites.a, type="sink")
#     base.add_boundary(base.metabolites.h_p, type="sink")
#     base.add_boundary(base.metabolites.h_c, type="sink")
#     base.add_boundary(base.metabolites.c, type="demand")
#     for met in base.metabolites:
#         met.compartment = 'c'
#     return base


@register_with(MODEL_REGISTRY)
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
    for met in base.metabolites:
        met.compartment = 'c'
    return base


@register_with(MODEL_REGISTRY)
def all_balanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
def mass_unbalanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=2)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
def charge_unbalanced(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=1)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
def met_no_formula(base):
    met_a = cobra.Metabolite("A", formula=None, charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2', charge=2)
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
def met_no_charge(base):
    met_a = cobra.Metabolite("A", formula='CHOPNS', charge=1)
    met_b = cobra.Metabolite("B", formula='C2H2O2P2N2S2')
    rxn1 = cobra.Reaction("RA1")
    rxn1.add_metabolites({met_a: -2, met_b: 1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
def loopless_toy_model(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABC"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["VA", "VB", "v1", "v2"]]
                       )
    base.reactions.VA.add_metabolites({"A": 1})
    base.reactions.VB.add_metabolites({"C": -1})
    base.reactions.v1.add_metabolites({"A": -1, "B": 1})
    base.reactions.v2.add_metabolites({"B": -1, "C": 1})
    base.reactions.v1.bounds = -1000, 1000
    base.reactions.v2.bounds = -1000, 1000
    base.objective = 'VB'
    base.reactions.VB.bounds = 0, 1
    return base


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
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


@register_with(MODEL_REGISTRY)
def producing_toy_model(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABCD"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["VA", "VB", "VD", "v1", "v2", "v3", "v4"]]
                       )
    base.reactions.VA.add_metabolites({"A": 1})
    base.reactions.VB.add_metabolites({"C": -1})
    base.reactions.VD.add_metabolites({"D": -1})
    base.reactions.v1.add_metabolites({"A": -1, "B": 1})
    base.reactions.v2.add_metabolites({"B": -1, "C": 1})
    base.reactions.v3.add_metabolites({"A": -1, "C": 1})
    base.reactions.v4.add_metabolites({"A": -1, "C": 1, "D": 1})
    base.reactions.v1.bounds = -1000, 1000
    base.reactions.v2.bounds = -1000, 1000
    base.reactions.v3.bounds = -1000, 1000
    base.reactions.v4.bounds = 0, 1
    base.objective = 'VB'
    base.reactions.VB.bounds = 0, 1
    return base


@register_with(MODEL_REGISTRY)
def consuming_toy_model(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "ABCD"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["VA", "VB", "VD", "v1", "v2", "v3", "v4"]]
                       )
    base.reactions.VA.add_metabolites({"A": 1})
    base.reactions.VB.add_metabolites({"C": -1})
    base.reactions.VD.add_metabolites({"D": -1})
    base.reactions.v1.add_metabolites({"A": -1, "B": 1})
    base.reactions.v2.add_metabolites({"B": -1, "C": 1})
    base.reactions.v3.add_metabolites({"A": -1, "C": 1})
    base.reactions.v4.add_metabolites({"A": -1, "C": 1, "D": -1})
    base.reactions.v1.bounds = -1000, 1000
    base.reactions.v2.bounds = -1000, 1000
    base.reactions.v3.bounds = -1000, 1000
    base.reactions.v4.bounds = -1, 0
    base.objective = 'VB'
    base.reactions.VB.bounds = 0, 1
    return base


@register_with(MODEL_REGISTRY)
def gap_model(base):
    a_c = cobra.Metabolite("a_c")
    a_e = cobra.Metabolite("a_e")
    b_c = cobra.Metabolite("b_c")
    c_c = cobra.Metabolite("c_c")
    base.add_metabolites([a_e])
    rxn1 = cobra.Reaction("R1")
    rxn1.add_metabolites({a_c: -1, b_c: 1})
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({a_c: -1, c_c: 1})
    base.add_reactions([rxn1, rxn2])
    return base


@register_with(MODEL_REGISTRY)
def gap_model_2(base):
    base.add_metabolites([cobra.Metabolite(i) for i in "abcd"])
    base.add_reactions([cobra.Reaction(i)
                        for i in ["EX_A", "A2B", "C2D", "EX_D"]])
    base.reactions.EX_A.add_metabolites({"a": 1})
    base.reactions.EX_D.add_metabolites({"d": -1})
    base.reactions.A2B.add_metabolites({"a": -1, "b": 1})
    base.reactions.C2D.add_metabolites({"c": -1, "d": 1})
    base.reactions.A2B.bounds = 0, 1000
    base.reactions.C2D.bounds = 0, 1000
    return base


@register_with(MODEL_REGISTRY)
def gapfilled_model(base):
    a_c = cobra.Metabolite("a_c")
    a_e = cobra.Metabolite("a_e")
    b_c = cobra.Metabolite("b_c")
    c_c = cobra.Metabolite("c_c")
    rxn1 = cobra.Reaction("R1")
    rxn1.add_metabolites({a_c: -1, b_c: 1})
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({a_c: -1, c_c: 1})
    rxn3 = cobra.Reaction("R3tec")
    rxn3.add_metabolites({a_e: -1, a_c: 1})
    rxn4 = cobra.Reaction("DM_b_c")
    rxn4.add_metabolites({b_c: -1})
    rxn5 = cobra.Reaction("DM_c_c")
    rxn5.add_metabolites({c_c: -1})
    rxn6 = cobra.Reaction("EX_a_e")
    rxn6.add_metabolites({a_e: 1})
    base.add_reactions([rxn1, rxn2, rxn3, rxn4, rxn5, rxn6])
    return base


@register_with(MODEL_REGISTRY)
def reversible_gap(base):
    a_c = cobra.Metabolite("a_c")
    b_c = cobra.Metabolite("b_c")
    c_c = cobra.Metabolite("c_c")
    rxn1 = cobra.Reaction("R1", lower_bound=-1000)
    rxn1.add_metabolites({a_c: -1, b_c: 1})
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({a_c: -1, c_c: 1})
    base.add_reactions([rxn1, rxn2])
    return base


@pytest.mark.parametrize("model, consistent", [
    ("textbook", True),
    ("figure_1", False),
    ("equation_8", False),
    ("figure_2", False),
], indirect=["model"])
def test_check_stoichiometric_consistency(model, consistent):
    assert consistency.check_stoichiometric_consistency(model) is consistent


@pytest.mark.parametrize("model, inconsistent", [
    ("textbook", []),
    ("figure_1", ["A'", "B'", "C'"]),
    ("equation_8", ["A", "B", "C"]),
    ("figure_2", ["X"]),
], indirect=["model"])
def test_find_unconserved_metabolites(model, inconsistent):
    unconserved_mets = consistency.find_unconserved_metabolites(model)
    assert set([met.id for met in unconserved_mets]) == set(inconsistent)


@pytest.mark.xfail(reason="Bug in current implementation.")
@pytest.mark.parametrize("model, inconsistent", [
    ("textbook", []),
    ("figure_1", [("A'",), ("B'",), ("C'",)]),
    ("equation_8", [("A",), ("B",), ("C",)]),
    ("figure_2", [("X",)]),
], indirect=["model"])
def test_find_inconsistent_min_stoichiometry(model, inconsistent):
    unconserved_sets = consistency.find_inconsistent_min_stoichiometry(model)
    for unconserved in unconserved_sets:
        assert tuple(met.id for met in unconserved) in set(inconsistent)


@pytest.mark.parametrize("model, metabolite_id", [
    # test control flow statements
    ("produces_atp", 'MNXM3'),
    ("produces_accoa", 'MNXM21'),
    ("produces_fadh2", "MNXM38"),
    ("produces_glu", "MNXM89557"),
    ("produces_nadh", "MNXM10"),
    ("maintenance_present", "MNXM3"),
], indirect=["model"])
def test_detect_energy_generating_cycles_control_flow(model, metabolite_id):
    """Expect that energy-generating cycles don't exist for metabolite ID."""
    cycle = consistency.detect_energy_generating_cycles(model, metabolite_id)
    assert set(cycle) == {'A', 'B', 'C'}


@pytest.mark.parametrize("model, metabolite_id, output", [
    # test for possible exceptions
    ("no_atp", "MNXM3", []),
    ("infeasible", "MNXM3", {'A', 'B', 'C'})
], indirect=["model"])
def test_detect_energy_generating_cycles_exceptions(model, metabolite_id,
                                                    output):
    """Expect that energy-generating cycles don't exist for metabolite ID."""
    result = consistency.detect_energy_generating_cycles(model, metabolite_id)
    assert set(result) == set(output)


@pytest.mark.parametrize("model, num", [
    ("all_balanced", 0),
    ("mass_unbalanced", 0),
    ("charge_unbalanced", 1),
    ("met_no_charge", 1),
    ("met_no_formula", 0)
], indirect=["model"])
def test_find_charge_unbalanced_reactions(model, num):
    """Expect all reactions to be charge balanced."""
    internal_rxns = con_helpers.get_internals(model)
    reactions = consistency.find_charge_unbalanced_reactions(internal_rxns)
    assert len(reactions) == num


@pytest.mark.parametrize("model, num", [
    ("all_balanced", 0),
    ("mass_unbalanced", 1),
    ("charge_unbalanced", 0),
    ("met_no_charge", 0),
    ("met_no_formula", 1)
], indirect=["model"])
def test_find_mass_unbalanced_reactions(model, num):
    """Expect all reactions to be mass balanced."""
    internal_rxns = con_helpers.get_internals(model)
    reactions = consistency.find_mass_unbalanced_reactions(internal_rxns)
    assert len(reactions) == num


@pytest.mark.parametrize("model, num", [
    ("loopy_toy_model", 3),
    ("loopless_toy_model", 0),
    ("infeasible_toy_model", 0),
], indirect=["model"])
def test_find_stoichiometrically_balanced_cycles(model, num):
    """Expect no stoichiometrically balanced loops to be present."""
    rxns_in_loops = consistency.find_stoichiometrically_balanced_cycles(
        model
    )
    assert len(rxns_in_loops) == num


@pytest.mark.parametrize("model, num", [
    ("gap_model", 1),
    ("gapfilled_model", 0),
    ("reversible_gap", 0)
], indirect=["model"])
def test_find_orphans(model, num):
    """Expect the appropriate amount of orphans to be found."""
    orphans = consistency.find_orphans(model)
    assert len(orphans) == num


@pytest.mark.parametrize("model, num", [
    ("gap_model", 2),
    ("gapfilled_model", 0),
    ("reversible_gap", 1)
], indirect=["model"])
def test_find_deadends(model, num):
    """Expect the appropriate amount of deadends to be found."""
    deadends = consistency.find_deadends(model)
    assert len(deadends) == num


@pytest.mark.parametrize("model, num", [
    ("gap_model", 1),
    ("gapfilled_model", 0),
], indirect=["model"])
def test_find_disconnected(model, num):
    """Expect the appropriate amount of disconnected to be found."""
    disconnected = consistency.find_disconnected(model)
    assert len(disconnected) == num


@pytest.mark.parametrize("model, num", [
    ("gap_model", 4),
    ("gap_model_2", 1),
    ("gapfilled_model", 0),
], indirect=['model'])
def test_find_metabolites_not_produced_with_open_bounds(model, num):
    """Expect the appropriate amount of nonproduced metabolites to be found."""
    badmets = consistency.find_metabolites_not_produced_with_open_bounds(model)
    assert len(badmets) == num


@pytest.mark.parametrize("model, num", [
    ("gap_model", 4),
    ("gap_model_2", 1),
    ("gapfilled_model", 0),
], indirect=['model'])
def test_find_metabolites_not_consumed_with_open_bounds(model, num):
    """Expect the appropriate amount of nonconsumed metabolites to be found."""
    badmets = consistency.find_metabolites_not_consumed_with_open_bounds(model)
    assert len(badmets) == num


@pytest.mark.parametrize("model, fraction", [
    ("blocked_reactions", 1.0),
    ("constrained_toy_model", 0.0),
    ("loopy_toy_model", 0.6)
], indirect=["model"])
def test_find_reactions_with_unbounded_flux_default_condition(model, fraction):
    """Expect the number of unbounded and blocked metabolites to be correct."""
    _, unb_fraction, _ = \
        consistency.find_reactions_with_unbounded_flux_default_condition(model)
    assert unb_fraction == fraction


@pytest.mark.parametrize("model", [
    pytest.param("missing_energy_partner",
                 marks=pytest.mark.raises(exception=ZeroDivisionError)),
    pytest.param("infeasible",
                 marks=pytest.mark.raises(exception=Infeasible))
], indirect=["model"])
def test_find_reactions_with_unbounded_flux_default_condition_errors(model):
    """Expect the number of unbounded and blocked metabolites to be correct."""
    consistency.find_reactions_with_unbounded_flux_default_condition(model)
