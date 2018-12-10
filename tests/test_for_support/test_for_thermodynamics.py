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


REACTION_REGISTRY = {}


@pytest.fixture(scope="module")
def metabolite_registry():
    registry = {}
    registry["g6p_c"] = cobra.Metabolite("g6p_c", compartment="c")
    registry["g6p_c"].annotation["kegg.compound"] = "C00668"
    registry["glc__D_c"] = cobra.Metabolite("glc__D_c", compartment="c")
    registry["glc__D_c"].annotation["kegg.compound"] = "C00267"
    registry["h2o_c"] = cobra.Metabolite("h2o_c", compartment="c")
    registry["h2o_c"].annotation["kegg.compound"] = "C00001"
    registry["pi_c"] = cobra.Metabolite("pi_c", compartment="c")
    registry["pi_c"].annotation["kegg.compound"] = "C00009"
    registry["h2o_c_list"] = cobra.Metabolite("h2o_c", compartment="c")
    registry["h2o_c_list"].annotation["kegg.compound"] = [
        'C00001', 'C01328', 'D00001', 'D03703', 'D06322']
    registry["o2_c_list"] = cobra.Metabolite("o2_c", compartment="c")
    registry["o2_c_list"].annotation["kegg.compound"] = ['C00007', 'D00003']
    registry["h2_c_list"] = cobra.Metabolite("h2_c", compartment="c")
    registry["h2_c_list"].annotation["kegg.compound"] = ['C00282']
    registry["h2o_c_name"] = cobra.Metabolite(
        "h2o_c", name="Water", compartment="c")
    registry["o2_c_name"] = cobra.Metabolite(
        "o2_c", name="Oxygen", compartment="c")
    registry["h2_c_name"] = cobra.Metabolite(
        "h2_c", name="Hydrogen", compartment="c")
    registry["whack_c"] = cobra.Metabolite(
        "whack_c", name="Whack", compartment="c")
    registry["odd_c"] = cobra.Metabolite("odd_c", name="Odd", compartment="c")
    registry["unknown_c"] = cobra.Metabolite("unknown_c", compartment="c")
    return registry


@pytest.fixture(scope="function")
def metabolite(request, metabolite_registry):
    return metabolite_registry[request.param]


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


@pytest.mark.parametrize("annotation, expected", [
    (["C00101", "C00099", "G12322"], "C00099"),
    pytest.param(["G12322"], None,
                 marks=pytest.mark.raises(exception=ValueError))
])
def test_get_smallest_compound_id(annotation, expected):
    """Expect the smallest KEGG compound identifier to be returned."""
    assert thermo.get_smallest_compound_id(annotation) == expected


@pytest.mark.parametrize("metabolite, kegg_id", [
    ("g6p_c", "C00668"),
    ("glc__D_c", "C00267"),
    ("h2o_c", "C00001"),
    ("pi_c", "C00009"),
    ("h2o_c_list", "C00001"),
    ("o2_c_list", "C00007"),
    ("h2_c_list", "C00282"),
    # We currently do not match names because it takes too long.
    # ("h2o_c_name", "C00001"),
    # ("o2_c_name", "C00007"),
    # ("h2_c_name", "C00282"),
    # Names instead should return nothing.
    ("h2o_c_name", None),
    ("o2_c_name", None),
    ("h2_c_name", None),
    ("whack_c", None),
    ("odd_c", None),
    ("unknown_c", None),
], indirect=["metabolite"])
def test_map_metabolite2kegg(metabolite, kegg_id):
    """Expect different forms of annotation to return the right thing."""
    assert thermo.map_metabolite2kegg(metabolite) == kegg_id


@pytest.mark.parametrize("reaction, expected", [
    ("direct_annotation",
     {"C00668": -1, "C00001": -1, "C00267": 1, "C00009": 1}),
    ("list_annotation",
     {"C00282": -2, "C00007": -1, "C00001": 1}),
    # We currently do not match names because it takes too long.
    # ("no_annotation_matching",
    #  {"C00282": -2, "C00007": -1, "C00001": 1}),
    # Names instead should return nothing.
    ("no_annotation_matching", {}),
    ("no_annotation_not_matching", {})
], indirect=["reaction"])
def test_translate_reaction(reaction, expected):
    """Expect the KEGG stoichiometry to match the expectation."""
    mapping = {}
    assert thermo.translate_reaction(reaction, mapping) == expected


@pytest.mark.parametrize("reaction, expected", [
    ("direct_annotation", (1, 0, 0, 0)),
    ("direct_annotation_correct_rev", (1, 0, 0, 0)),
    ("list_annotation", (0, 0, 0, 1)),
    # We currently do not match names because it takes too long.
    # ("no_annotation_matching", (0, 0, 0, 1)),
    # Names instead should return nothing.
    ("no_annotation_matching", (0, 1, 0, 0)),
    ("no_annotation_not_matching", (0, 1, 0, 0)),
    ("problematic_metabolites", (0, 0, 1, 0))
], indirect=["reaction"])
def test_find_incorrect_thermodynamic_reversibility(reaction, expected):
    """Expect the correct reversibility information."""
    result = tuple(map(
        len, thermo.find_thermodynamic_reversibility_index([reaction])))
    assert result == expected
