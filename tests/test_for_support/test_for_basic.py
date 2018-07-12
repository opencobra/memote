# -*- coding: utf-8 -*-

# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability,
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

"""Ensure the expected functioning of ``memote.support.basic``."""

from __future__ import absolute_import

import cobra
import pytest

import memote.support.basic as basic
import memote.support.helpers as helpers
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def three_missing(base):
    base.add_metabolites([cobra.Metabolite(id="M{0:d}".format(i))
                          for i in range(1, 4)])
    return base


@register_with(MODEL_REGISTRY)
def three_present(base):
    base.add_metabolites(
        [cobra.Metabolite(id="M{0:d}".format(i), formula="CH4", charge=-1)
         for i in range(1, 4)]
    )
    return base


@register_with(MODEL_REGISTRY)
def gpr_present(base):
    """Provide a model with reactions that all have GPR"""
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.gene_reaction_rule = 'gene1 or gene2'
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def gpr_present_complex(base):
    """Provide a model with reactions that all have GPR"""
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.gene_reaction_rule = 'gene1 and gene2'
    rxn_2 = cobra.Reaction("RXN2")
    rxn_2.gene_reaction_rule = '(gene4 and gene7) or ' \
                               '(gene9 and (gene10 or gene14))'
    rxn_3 = cobra.Reaction("RXN3")
    rxn_3.gene_reaction_rule = 'gene1 and gene2'
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


@register_with(MODEL_REGISTRY)
def gpr_missing(base):
    """Provide a model reactions that lack GPR"""
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def gpr_missing_with_exchange(base):
    """Provide a model reactions that lack GPR"""
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_2 = cobra.Reaction("EX_met1_c")
    met_1 = cobra.Metabolite("met1")
    rxn_2.add_metabolites({met_1: 1})
    base.add_reactions([rxn_1, rxn_2])
    return base


@register_with(MODEL_REGISTRY)
def gpr_present_not_lumped(base):
    """Provide a model with reactions that all have GPR"""
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.gene_reaction_rule = 'gene1'
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def unconstrained_rxn(base):
    """Provide a model with one unconstrained reaction"""
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_1.bounds = -1000, 1000
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def irreversible_rxn(base):
    """Provide a model with one irreversible reaction"""
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_1.bounds = 0, 1000
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def zero_constrained_rxn(base):
    """Provide a model with one zero-constrained reaction"""
    rxn_1 = cobra.Reaction("RXN1")
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_1.bounds = 0, 0
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def nonzero_constrained_rxn(base):
    """Provide a model with one nonzero-constrained reaction"""
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    met_3 = cobra.Metabolite("met3")
    met_4 = cobra.Metabolite("met4")
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_2 = cobra.Reaction("RXN2")
    rxn_2.add_metabolites({met_2: -1, met_3: -1})
    rxn_3 = cobra.Reaction("RXN3")
    rxn_3.add_metabolites({met_3: -1, met_4: 1})
    rxn_1.bounds = -1000, 1000
    rxn_2.bounds = -1000, 1000
    rxn_3.bounds = 0, 10
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


@register_with(MODEL_REGISTRY)
def no_nonzero_constrained_rxn(base):
    """Provide a model with no nonzero-constrained reactions"""
    met_1 = cobra.Metabolite("met1")
    met_2 = cobra.Metabolite("met2")
    met_3 = cobra.Metabolite("met3")
    met_4 = cobra.Metabolite("met4")
    rxn_1 = cobra.Reaction("RXN1")
    rxn_1.add_metabolites({met_1: 1, met_2: -1})
    rxn_2 = cobra.Reaction("RXN2")
    rxn_2.add_metabolites({met_2: -1, met_3: -1})
    rxn_3 = cobra.Reaction("RXN3")
    rxn_3.add_metabolites({met_3: -1, met_4: 1})
    rxn_1.bounds = -1000, 1000
    rxn_2.bounds = -1000, 1000
    rxn_3.bounds = 0, 1000
    base.add_reactions([rxn_1, rxn_2, rxn_3])
    return base


@register_with(MODEL_REGISTRY)
def ngam_present(base):
    """Provide a model with a correct NGAM reaction"""
    met_g = cobra.Metabolite("atp_c", "C10H12N5O13P3", compartment="c")
    met_h = cobra.Metabolite("adp_c", "C10H12N5O10P2", compartment="c")
    met_i = cobra.Metabolite("h_c", "H", compartment="c")
    met_j = cobra.Metabolite("h2o_c", "H2O", compartment="c")
    met_k = cobra.Metabolite("pi_c", "HO4P", compartment="c")
    rxn_1 = cobra.Reaction("ATPM", name="non-growth associated maintenance")
    rxn_1.add_metabolites({met_g: -1, met_h: 1, met_i: 1, met_j: -1, met_k: 1})
    rxn_1.lower_bound = 8.39
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def ngam_and_atpsynthase(base):
    """Provide a model with an ATP hydrolysis and an NGAM reaction"""
    met_g = cobra.Metabolite("atp_c", "C10H12N5O13P3", compartment="c")
    met_h = cobra.Metabolite("adp_c", "C10H12N5O10P2", compartment="c")
    met_i = cobra.Metabolite("h_e", "H", compartment="e")
    met_j = cobra.Metabolite("h2o_c", "H2O", compartment="c")
    met_k = cobra.Metabolite("pi_c", "HO4P", compartment="c")
    met_l = cobra.Metabolite("h_c", "H", compartment="c")
    rxn_1 = cobra.Reaction("ATPS", name="ATPase cytosolic")
    rxn_1.add_metabolites({met_g: -1, met_h: 1, met_i: 1, met_j: -1, met_k: 1})
    rxn_1.bounds = -1000, 1000
    rxn_2 = cobra.Reaction("NGAM", name="non-growth associated maintenance")
    rxn_2.add_metabolites({met_g: -1, met_h: 1, met_l: 1, met_j: -1, met_k: 1})
    rxn_2.bounds = 0, 1000
    base.add_reactions([rxn_1, rxn_2])
    return base


@register_with(MODEL_REGISTRY)
def sufficient_compartments(base):
    """Provide a model with the minimal amount of compartments"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("a_p", compartment="p")
    met_c = cobra.Metabolite("a_e", compartment="e")
    rxn_a_b = cobra.Reaction("AB")
    rxn_a_b.add_metabolites({met_a: 1, met_b: -1})
    rxn_b_c = cobra.Reaction("BC")
    rxn_b_c.add_metabolites({met_b: 1, met_c: -1})
    base.add_reactions([rxn_b_c, rxn_a_b])
    return base


@register_with(MODEL_REGISTRY)
def insufficient_compartments(base):
    """Provide a model with less than the minimal amount of compartments"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_c = cobra.Metabolite("a_e", compartment="e")
    rxn_a_c = cobra.Reaction("AC")
    rxn_a_c.add_metabolites({met_a: 1, met_c: -1})
    base.add_reactions([rxn_a_c])
    return base


@register_with(MODEL_REGISTRY)
def non_metabolic_reactions(base):
    """Provide a model all kinds of reactions that are not purely metabolic"""
    met_a = cobra.Metabolite("a_c", formula='CH4', compartment="c")
    met_c = cobra.Metabolite("a_e", formula='CH4', compartment="e")
    rxn_a_c = cobra.Reaction("AC")
    rxn_a_c.add_metabolites({met_a: 1, met_c: -1})
    biomass = cobra.Reaction("BIOMASS")
    ex_a = cobra.Reaction("EX_a_e")
    ex_a.add_metabolites({met_c: -1})
    base.add_reactions([rxn_a_c, biomass, ex_a])
    return base


@register_with(MODEL_REGISTRY)
def transport_gpr(base):
    """Provide a model with a transport reaction without GPR."""
    met_a = cobra.Metabolite("co2_c", formula='CO2', compartment="c")
    met_b = cobra.Metabolite("co2_e", formula='CO2', compartment="e")
    met_c = cobra.Metabolite("na_c", formula='Na', compartment="c")
    met_d = cobra.Metabolite("na_e", formula='Na', compartment="e")
    uni = cobra.Reaction("UNI")
    uni.gene_reaction_rule="X and Y"
    uni.add_metabolites({met_a: 1, met_b: -1})
    anti = cobra.Reaction("ANTI")
    anti.gene_reaction_rule = "W or V"
    anti.add_metabolites({met_a: 1, met_d: 1, met_b: -1, met_c: -1})
    sym = cobra.Reaction("SYM")
    sym.add_metabolites({met_a: 1, met_c: 1, met_b: -1, met_d: -1})
    base.add_reactions([uni, anti, sym])
    return base


@register_with(MODEL_REGISTRY)
def transport_gpr_constrained(base):
    """Provide a model with a constrained transport reaction without GPR."""
    met_a = cobra.Metabolite("co2_c", formula='CO2', compartment="c")
    met_b = cobra.Metabolite("co2_e", formula='CO2', compartment="e")
    met_c = cobra.Metabolite("na_c", formula='Na', compartment="c")
    met_d = cobra.Metabolite("na_e", formula='Na', compartment="e")
    uni = cobra.Reaction("UNI")
    uni.gene_reaction_rule="X and Y"
    uni.add_metabolites({met_a: 1, met_b: -1})
    anti = cobra.Reaction("ANTI")
    anti.gene_reaction_rule = "W or V"
    anti.add_metabolites({met_a: 1, met_d: 1, met_b: -1, met_c: -1})
    sym = cobra.Reaction("SYM")
    sym.add_metabolites({met_a: 1, met_c: 1, met_b: -1, met_d: -1})
    sym.lower_bound = 8.39
    base.add_reactions([uni, anti, sym])
    return base


@register_with(MODEL_REGISTRY)
def reversible_oxygen_flow(base):
    """Provide a model with a reversible oxygen-containing reaction."""
    met_a = cobra.Metabolite("o2s_e", formula="O2", compartment="e")
    met_b = cobra.Metabolite("o2s_p", formula="O2", compartment="p")
    rxn = cobra.Reaction("O2Stex")
    rxn.add_metabolites({met_a: -1, met_b: 1})
    rxn.lower_bound = -1000
    rxn.upper_bound = 1000
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def non_reversible_oxygen_flow(base):
    """Provide a model with a non-reversible oxygen-containing reaction."""
    met_a = cobra.Metabolite("o2s_c", formula="O2", compartment="c")
    met_b = cobra.Metabolite("o2_c", formula="O2", compartment="c")
    met_c = cobra.Metabolite("h2o2_c", formula='H2O2', compartment="c")
    met_i = cobra.Metabolite("h_c", "H", compartment="c")
    rxn = cobra.Reaction("SPODM")
    rxn.add_metabolites({met_a: -2, met_b: 1, met_c: 1, met_i: -2})
    rxn.lower_bound = 0
    rxn.upper_bound = 0
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def dup_mets_in_c(base):
    """Provide a model with duplicate metabolites in the same compartment"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    dup_a = cobra.Metabolite("x_c", compartment="c")
    not_a = cobra.Metabolite("b_c", compartment="c")

    met_a.annotation["inchikey"] = "1231"
    met_a.annotation["kegg"] = "123"
    dup_a.annotation["inchikey"] = "1231"
    dup_a.annotation["kegg"] = "123"
    not_a.annotation["inchikey"] = "3211"
    not_a.annotation["kegg"] = "321"

    met_b = cobra.Metabolite("a_p", compartment="p")
    met_c = cobra.Metabolite("a_e", compartment="e")
    rxn_a_b = cobra.Reaction("AB")
    rxn_a_b.add_metabolites({dup_a: 1, met_a: 1, met_b: -1})
    rxn_b_c = cobra.Reaction("BC")
    rxn_b_c.add_metabolites({not_a: 1, met_b: 1, met_c: -1})
    base.add_reactions([rxn_b_c, rxn_a_b])
    return base


@register_with(MODEL_REGISTRY)
def dup_mets_in_c_wrong_annotation(base):
    """Provide a model like `dup_mets_in_c` but with improper annotations"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    dup_a = cobra.Metabolite("x_c", compartment="c")
    not_a = cobra.Metabolite("b_c", compartment="c")

    met_a.annotation["kegg"] = "123"
    dup_a.annotation["kegg"] = "123"
    not_a.annotation["kegg"] = "321"

    met_b = cobra.Metabolite("a_p", compartment="p")
    met_c = cobra.Metabolite("a_e", compartment="e")
    rxn_a_b = cobra.Reaction("AB")
    rxn_a_b.add_metabolites({dup_a: 1, met_a: 1, met_b: -1})
    rxn_b_c = cobra.Reaction("BC")
    rxn_b_c.add_metabolites({not_a: 1, met_b: 1, met_c: -1})
    base.add_reactions([rxn_b_c, rxn_a_b])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns(base):
    """Provide a model with duplicate reactions"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = "HEX"
    dup_1.annotation["kegg.reaction"] = "HEX"
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns_multiple_anns(base):
    """Provide a model like `dup_rxns` but with multiple annotations per rxn"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = "HEX"
    rxn_1.annotation["metanetx.reaction"] = "MNXR1"
    dup_1.annotation["kegg.reaction"] = "HEX"
    dup_1.annotation["metanetx.reaction"] = "MNXR1"
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns_partial_matching_multiple_anns(base):
    """Provide a model like `dup_rxns_multiple_anns` but with partial matches"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = "HEX"
    rxn_1.annotation["metanetx.reaction"] = "MNXR1"
    dup_1.annotation["kegg.reaction"] = "HEX"
    dup_1.annotation["metanetx.reaction"] = "MNXR2"
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns_no_matching_multiple_anns(base):
    """Provide a model like `dup_rxns_multiple_anns` but with no matches"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = "HEX11"
    rxn_1.annotation["metanetx.reaction"] = "MNXR11"
    dup_1.annotation["kegg.reaction"] = "HEX22"
    dup_1.annotation["metanetx.reaction"] = "MNXR22"
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns_list_anns(base):
    """Provide a model like `dup_rxns` but with list annotations"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = ["HEX11", "HEX22"]
    dup_1.annotation["kegg.reaction"] = "HEX22"
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns_multiple_list_anns(base):
    """Provide a model like `dup_rxns_multiple_anns` but with list anns"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = ["HEX11", "HEX22"]
    dup_1.annotation["kegg.reaction"] = ["HEX22", "HEX11"]
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def dup_rxns_multiple_list_anns_no_match(base):
    """Provide a model like `dup_rxns_multiple_list_anns` but with no match"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    dup_1 = cobra.Reaction("dup1")
    rxn_1.annotation["kegg.reaction"] = ["HEX111", "HEX222"]
    dup_1.annotation["kegg.reaction"] = ["HEX221", "HEX112"]
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    dup_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1, dup_1])
    return base


@register_with(MODEL_REGISTRY)
def rxns_no_exchange(base):
    """Provide a model with no exchange reactions"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1])
    return base


@register_with(MODEL_REGISTRY)
def rxns_with_two_substrates(base):
    """Provide a model with two substrates that can be taken up"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    met_c = cobra.Metabolite("c_e", compartment="e")
    met_d = cobra.Metabolite("d_e", compartment="e")
    rxn_1 = cobra.Reaction("rxn1")
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1])
    base.add_boundary(
        met_c, type="custom", reaction_id="EX_c", lb=-1000, ub=1000)
    base.add_boundary(
        met_d, type="custom", reaction_id="EX_d", lb=-1000, ub=1000)
    return base


@register_with(MODEL_REGISTRY)
def rxns_with_two_false_substrates(base):
    """Provide a model with two false substrates that cannot be taken up"""
    met_a = cobra.Metabolite("a_c", compartment="c")
    met_b = cobra.Metabolite("b_c", compartment="c")
    met_c = cobra.Metabolite("c_e", compartment="c")
    met_d = cobra.Metabolite("d_e", compartment="c")
    rxn_1 = cobra.Reaction("rxn1")
    rxn_1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn_1])
    base.add_boundary(met_c, type="custom", reaction_id="EX_c", lb=1, ub=1000)
    base.add_boundary(met_d, type="custom", reaction_id="EX_d", lb=1, ub=1000)
    return base


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("three_missing", 3),
    ("three_present", 0)
], indirect=["model"])
def test_metabolites_formula_presence(model, num):
    """Expect all metabolites to have a formula."""
    assert len(basic.check_metabolites_formula_presence(model)) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("three_missing", 3),
    ("three_present", 0)
], indirect=["model"])
def test_metabolites_charge_presence(model, num):
    """Expect all metabolites to have a charge."""
    assert len(basic.check_metabolites_charge_presence(model)) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("gpr_present", 0),
    ("gpr_missing", 1),
    ("gpr_missing_with_exchange", 1),
], indirect=["model"])
def test_gene_protein_reaction_rule_presence(model, num):
    """Expect all non-exchange reactions to have a GPR."""
    missing_gpr_metabolic_rxns = \
        set(
            basic.check_gene_protein_reaction_rule_presence(
                model
            )
        ).difference(set(model.boundary))
    assert len(missing_gpr_metabolic_rxns) == num


@pytest.mark.parametrize("model, coverage", [
    pytest.param("empty", 0,
                 marks=pytest.mark.raises(exception=ValueError)),
    ("gpr_present", 0.5),
    ("gpr_present_not_lumped", 1),
], indirect=["model"])
def test_metabolic_coverage(model, coverage):
    """Expect a model to have high metabolic coverage."""
    metabolic_coverage = basic.calculate_metabolic_coverage(model)
    assert metabolic_coverage >= coverage


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("unconstrained_rxn", 0),
    ("nonzero_constrained_rxn", 1),
    ("no_nonzero_constrained_rxn", 0),
], indirect=["model"])
def test_find_nonzero_constrained_reactions(model, num):
    """Expect amount of non-zero rxns to be identified correctly."""
    nonzero_constrained_rxns = basic.find_nonzero_constrained_reactions(model)
    assert len(nonzero_constrained_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("unconstrained_rxn", 0),
    ("zero_constrained_rxn", 1),
], indirect=["model"])
def test_find_zero_constrained_reactions(model, num):
    """Expect amount of zero-constrained rxns to be identified correctly."""
    zero_constrained_rxns = basic.find_zero_constrained_reactions(model)
    assert len(zero_constrained_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("unconstrained_rxn", 0),
    ("irreversible_rxn", 1),
], indirect=["model"])
def test_find_irreversible_reactions(model, num):
    """Expect amount of irreversible rxns to be identified correctly."""
    irreversible_rxns = basic.find_irreversible_reactions(model)
    assert len(irreversible_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("unconstrained_rxn", 1),
    ("zero_constrained_rxn", 0),
], indirect=["model"])
def test_find_unconstrained_reactions(model, num):
    """Expect amount of unconstrained rxns to be identified correctly."""
    unconstrained_rxns = basic.find_unconstrained_reactions(model)
    assert len(unconstrained_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("ngam_present", 1),
    ("ngam_and_atpsynthase", 1)
], indirect=["model"])
def test_ngam_presence(model, num):
    """Expect a single non growth-associated maintenance reaction."""
    ngam_reaction = basic.find_ngam(model)
    assert len(ngam_reaction) == num


@pytest.mark.parametrize("model, boolean", [
    ("sufficient_compartments", True),
    ("insufficient_compartments", False)
], indirect=["model"])
def test_compartments_presence(model, boolean):
    """Expect amount of compartments to be identified correctly."""
    assert (len(model.get_metabolite_compartments()) >= 3) == boolean


@pytest.mark.parametrize("model, num", [
    ("gpr_present", 0),
    ("gpr_missing", 0),
    ("gpr_present_complex", 4)
], indirect=["model"])
def test_enzyme_complex_presence(model, num):
    """Expect amount of enzyme complexes to be identified correctly."""
    assert len(basic.find_protein_complexes(model)) == num


# TODO: ngam_and_atpsynthase is not a proper positive control test model
# It needs to be replaced with a new test.
@pytest.mark.parametrize("model, num", [
    ("ngam_and_atpsynthase", 2),
    ("gpr_missing_with_exchange", 1),
    ("non_metabolic_reactions", 0)
], indirect=["model"])
def test_find_pure_metabolic_reactions(model, num):
    """Expect amount of metabolic reactions to be identified correctly."""
    assert len(basic.find_pure_metabolic_reactions(model)) == num


@pytest.mark.parametrize("model, num", [
    ("ngam_present", 1),
    ("ngam_and_atpsynthase", 0),
    ("non_metabolic_reactions", 0)
], indirect=["model"])
def test_find_constrained_pure_metabolic_reactions(model, num):
    """Expect num of contrained metabolic rxns to be identified correctly."""
    pmr = basic.find_pure_metabolic_reactions(model)
    contrained_pmr = set(
        [rxn for rxn in pmr if basic.is_constrained_reaction(model, rxn)])
    assert len(contrained_pmr) == num


@pytest.mark.parametrize("model, num", [
    ("transport_gpr_constrained", 1),
    ("transport_gpr", 0),
    ("ngam_and_atpsynthase", 0)
], indirect=["model"])
def test_find_constrained_transport_reactions(model, num):
    """Expect num of contrained transport rxns to be identified correctly."""
    transporters = helpers.find_transport_reactions(model)
    constrained_transporters = set(
        [rxn for rxn in transporters if basic.is_constrained_reaction(
            model, rxn)])
    assert len(constrained_transporters) == num


@pytest.mark.parametrize("model, num", [
    ("reversible_oxygen_flow", 1),
    ("non_reversible_oxygen_flow", 0),
    ("transport_gpr", 0)
], indirect=["model"])
def test_find_reversible_oxygen_reactions(model, num):
    """Expect amount of reversible O2 reactions to be identified correctly."""
    o2_rxns = basic.find_oxygen_reactions(model)
    rev_o2_rxns = [rxn for rxn in o2_rxns if rxn.reversibility]
    assert len(rev_o2_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("sufficient_compartments", 1)
], indirect=["model"])
def test_find_unique_metabolites(model, num):
    """Expect amount of metabolic reactions to be identified correctly."""
    assert len(basic.find_unique_metabolites(model)) == num


@pytest.mark.parametrize("model, num", [
    ("dup_mets_in_c", 1),
    ("dup_mets_in_c_wrong_annotation", 0),
    ("gpr_missing", 0)
], indirect=["model"])
def test_find_duplicate_metabolites_in_compartments(model, num):
    """Expect amount of duplicate metabolites to be identified correctly."""
    assert len(basic.find_duplicate_metabolites_in_compartments(model)) == num


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
    ("dup_rxns", 1),
    ("dup_rxns_multiple_anns", 1),
    ("dup_rxns_partial_matching_multiple_anns", 1),
    ("dup_rxns_list_anns", 1),
    ("dup_rxns_multiple_list_anns", 1),
    ("dup_rxns_no_matching_multiple_anns", 0),
    ("dup_rxns_multiple_list_anns_no_match", 0),
    ("gpr_missing", 0)
], indirect=["model"])
def test_find_duplicate_reactions(model, num):
    """Expect amount of duplicate metabolites to be identified correctly."""
    assert len(basic.find_duplicate_reactions(model)) == num


@pytest.mark.parametrize("model, num", [
    ("transport_gpr", 1)
], indirect=["model"])
def test_check_transport_reaction_gpr_presence(model, num):
    """Expect amount of transport reactions without gpr to be identified."""
    assert len(basic.check_transport_reaction_gpr_presence(model)) == num


@pytest.mark.parametrize("model, num", [
    ("rxns_with_two_substrates", 2),
    ("rxns_with_two_false_substrates", 0),
    ("rxns_no_exchange", 0),
], indirect=["model"])
def test_find_medium_metabolites(model, num):
    """Expect amount of medium metabolites be identified."""
    assert len(basic.find_medium_metabolites(model)) == num
