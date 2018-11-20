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

"""Ensure the expected functioning of ``memote.support.thermodynamics``."""

from __future__ import absolute_import

from sys import version_info

import cobra
import pytest

if version_info[:2] < (3, 5):
    pytest.skip("Thermodynamic tests require at least Python version 3.5.",
                allow_module_level=True)

import memote.support.thermodynamics as thermo
from memote.utils import register_with

REACTION_REGISTRY = dict()


@register_with(REACTION_REGISTRY)
def direct_annotation():
    """Provide a reaction where each met maps to a single KEGG compound ID."""
    a = cobra.Metabolite("g6p_c", compartment="c")
    a.annotation["kegg.compound"] = "C00668"
    b = cobra.Metabolite("glc__D_c", compartment="c")
    b.annotation["kegg.compound"] = "C00267"
    c = cobra.Metabolite("h2o_c", compartment="c")
    c.annotation["kegg.compound"] = "C00001"
    d = cobra.Metabolite("pi_c", compartment="c")
    d.annotation["kegg.compound"] = "C00009"
    r = cobra.Reaction("G6PP")
    r.add_metabolites({a: -1, c: -1, b: 1, d: 1})
    return r


@register_with(REACTION_REGISTRY)
def direct_annotation_correct_rev():
    """Provide a reaction where each met maps to a single KEGG compound ID."""
    a = cobra.Metabolite("g6p_c", compartment="c")
    a.annotation["kegg.compound"] = "C00668"
    b = cobra.Metabolite("glc__D_c", compartment="c")
    b.annotation["kegg.compound"] = "C00267"
    c = cobra.Metabolite("h2o_c", compartment="c")
    c.annotation["kegg.compound"] = "C00001"
    d = cobra.Metabolite("pi_c", compartment="c")
    d.annotation["kegg.compound"] = "C00009"
    r = cobra.Reaction("G6PP")
    r.add_metabolites({a: -1, c: -1, b: 1, d: 1})
    r.bounds = -1000, 1000
    return r


@register_with(REACTION_REGISTRY)
def list_annotation():
    """Provide a reaction where one met maps to several KEGG IDs."""
    c = cobra.Metabolite("h2o_c", compartment="c")
    c.annotation["kegg.compound"] = ['C00001', 'C01328', 'D00001',
                                     'D03703', 'D06322']
    d = cobra.Metabolite("o2_c", compartment="c")
    d.annotation["kegg.compound"] = ['C00007', 'D00003']
    e = cobra.Metabolite("h2_c", compartment="c")
    e.annotation["kegg.compound"] = 'C00282'
    r = cobra.Reaction("OxyHydrogenRxn")
    r.add_metabolites({d: -1, e: -2, c: 1})
    return r


@register_with(REACTION_REGISTRY)
def no_annotation_matching():
    """Provide a reaction where one met maps to several KEGG IDs."""
    c = cobra.Metabolite("h2o_c", name="Water", compartment="c")
    d = cobra.Metabolite("o2_c", name="Oxygen", compartment="c")
    e = cobra.Metabolite("h2_c", name="Hydrogen", compartment="c")
    r = cobra.Reaction("OxyHydrogenRxn")
    r.add_metabolites({d: -1, e: -2, c: 1})
    return r


@register_with(REACTION_REGISTRY)
def no_annotation_not_matching():
    """Provide a reaction where one met maps to several KEGG IDs."""
    c = cobra.Metabolite("whack_c", name="Whack", compartment="c")
    d = cobra.Metabolite("odd_c", name="Odd", compartment="c")
    e = cobra.Metabolite("unknown_c", compartment="c")
    r = cobra.Reaction("Foreign")
    r.add_metabolites({d: -1, e: -2, c: 1})
    return r


@register_with(REACTION_REGISTRY)
def problematic_metabolites():
    """Provide a reaction where some met cause problems in calculation."""
    a = cobra.Metabolite("frdp_c", compartment="c")
    a.annotation["kegg.compound"] = "C00448"
    b = cobra.Metabolite("h20_c", compartment="c")
    b.annotation["kegg.compound"] = "C00001"
    c = cobra.Metabolite("pheme_c", compartment="c")
    c.annotation["kegg.compound"] = "C00032"
    d = cobra.Metabolite("hemeO_c", compartment="c")
    d.annotation["kegg.compound"] = "C15672"
    e = cobra.Metabolite("ppi_c", compartment="c")
    e.annotation["kegg.compound"] = "C00013"
    r = cobra.Reaction("Heme O synthase")
    r.add_metabolites({a: -1, b: -1, c: -1, d: 1, e: 1})
    return r


@pytest.mark.parametrize("input, expected", [
    (["C00101", "C00099", "G12322"], ["C00099", "C00101"]),
    (["G12322"], [])])
def test_smallest_compound_ID(input, expected):
    """Expect shortened and sorted list to be returned correctly."""
    assert thermo.smallest_compound_id(input) == expected


@pytest.mark.parametrize("reaction, expected", [
    ("direct_annotation", "C00668 + C00001 -> C00267 + C00009"),
    ("list_annotation", "2 C00282 + C00007 -> C00001"),
    ("no_annotation_matching", "2 C00282 + C00007 -> C00001"),
    ("no_annotation_not_matching", "odd_c + 2 unknown_c -> whack_c")],
    indirect=["reaction"])
def test_get_equilibrator_rxn_string(reaction, expected):
    """Expect KEGG reaction string to match the expectation."""
    mapping_dict = thermo.get_metabolite_mapping([reaction])
    eq_rxn_string = thermo.get_equilibrator_reaction_string(reaction, mapping_dict)
    assert eq_rxn_string == expected


@pytest.mark.parametrize("reaction, expected", [
    ("direct_annotation", (1, 0, 0, 0)),
    ("direct_annotation_correct_rev", (0, 0, 0, 0)),
    ("list_annotation", (0, 0, 0, 1)),
    ("no_annotation_matching", (0, 0, 0, 1)),
    ("no_annotation_not_matching", (0, 1, 0, 0)),
    ("problematic_metabolites", (0, 0, 1, 0))],
    indirect=["reaction"])
def test_find_incorrect_thermodynamic_reversibility(reaction, expected):
    """Expect KEGG reaction string to match the expectation."""
    reactions = [reaction]
    rev, map, calc, bal = \
        thermo.find_incorrect_thermodynamic_reversibility(reactions)
    result = (len(rev), len(map), len(calc), len(bal))
    assert result == expected
