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

"""Ensure the expected functioning of ``memote.support.helpers``."""

from __future__ import absolute_import

import cobra
import pytest

import memote.support.helpers as helpers
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def uni_anti_symport(base):
    """Provide a model with 3 simple transport reactions."""
    met_a = cobra.Metabolite("co2_c", formula='CO2', compartment="c")
    met_b = cobra.Metabolite("co2_e", formula='CO2', compartment="e")
    met_c = cobra.Metabolite("na_c", formula='Na', compartment="c")
    met_d = cobra.Metabolite("na_e", formula='Na', compartment="e")
    uni = cobra.Reaction("UNI")
    uni.add_metabolites({met_a: 1, met_b: -1})
    anti = cobra.Reaction("ANTI")
    anti.add_metabolites({met_a: 1, met_d: 1, met_b: -1, met_c: -1})
    sym = cobra.Reaction("SYM")
    sym.add_metabolites({met_a: 1, met_c: 1, met_b: -1, met_d: -1})
    base.add_reactions([uni, anti, sym])
    return base


@register_with(MODEL_REGISTRY)
def abc_pump(base):
    """Provide a model with an ABC transport reaction."""
    atp = cobra.Metabolite("atp_c", formula='C10H12N5O13P3', compartment="c")
    adp = cobra.Metabolite("adp_c", formula='C10H12N5O10P2', compartment="c")
    h = cobra.Metabolite("h_c", formula='H', compartment="c")
    pi = cobra.Metabolite("pi_c", formula='HO4P', compartment="c")
    h2o = cobra.Metabolite("h2o_c", formula='H2O', compartment="c")
    aso_c = cobra.Metabolite("aso3_c", formula='AsO3', compartment="c")
    aso_e = cobra.Metabolite("aso3_e", formula='AsO3', compartment="e")
    pump = cobra.Reaction("PUMP")
    pump.add_metabolites({aso_c: -1, atp: -1, h2o: -1,
                          adp: 1, h: 1, pi: 1, aso_e: 1})
    base.add_reactions([pump])
    return base


@register_with(MODEL_REGISTRY)
def proton_pump(base):
    """Provide a model with an ABC proton pump reaction."""
    atp = cobra.Metabolite("atp_c", formula='C10H12N5O13P3', compartment="c")
    adp = cobra.Metabolite("adp_c", formula='C10H12N5O10P2', compartment="c")
    h_c = cobra.Metabolite("h_c", formula='H', compartment="c")
    pi = cobra.Metabolite("pi_c", formula='HO4P', compartment="c")
    h2o = cobra.Metabolite("h2o_c", formula='H2O', compartment="c")
    h_p = cobra.Metabolite("h_p", formula='H', compartment="p")
    pump = cobra.Reaction("PUMP")
    pump.add_metabolites({h_c: -4, adp: -1, pi: -1,
                          atp: 1, h2o: 1, h_p: 3})
    base.add_reactions([pump])
    return base


@register_with(MODEL_REGISTRY)
def phosphotransferase_system(base):
    """Provide a model with a PTS transport reaction."""
    pep = cobra.Metabolite("pep_c", formula='C3H2O6P', compartment="c")
    pyr = cobra.Metabolite("pyr_c", formula='C3H3O3', compartment="c")
    malt = cobra.Metabolite(",malt_e", formula='C12H22O11', compartment="e")
    malt6p = cobra.Metabolite(
        "malt6p_c", formula='C12H21O14P', compartment="c"
    )
    pst = cobra.Reaction("PST")
    pst.add_metabolites({pep: -1, malt: -1, pyr: 1, malt6p: 1})
    base.add_reactions([pst])
    return base


@register_with(MODEL_REGISTRY)
def energy_transfer(base):
    """Provide a model with a membrane-spanning electron transfer reaction."""
    cytaox = cobra.Metabolite("cytaox_c", formula='X', compartment="c")
    cytared = cobra.Metabolite("cytared_c", formula='XH2', compartment="c")
    cytbox = cobra.Metabolite("cytbox_m", formula='X', compartment="m")
    cytbred = cobra.Metabolite("cytbred_m", formula='XH2', compartment="m")
    et = cobra.Reaction("ET")
    et.add_metabolites({cytaox: -1, cytbred: -1, cytared: 1, cytbox: 1})
    base.add_reactions([et])
    return base


@register_with(MODEL_REGISTRY)
def converting_reactions(base):
    """Provide a model with a couple of converting reaction."""
    a = cobra.Metabolite("a_c")
    b = cobra.Metabolite("b_c")
    c = cobra.Metabolite("c_c")
    c2 = cobra.Metabolite("c_e")
    c3 = cobra.Metabolite("c_p")
    rxn1 = cobra.Reaction("R1")
    rxn1.add_metabolites({a: -1, b: 1})
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({a: -1, c: -1, b: 1, c2: 1})
    rxn3 = cobra.Reaction("R3")
    rxn3.add_metabolites({a: -1, c3: 1, c2: 1})
    base.add_reactions([rxn1, rxn2, rxn3])
    return base


@pytest.mark.parametrize("model, num", [
    ("uni_anti_symport", 3),
    ("abc_pump", 1),
    ("proton_pump", 1),
    ("energy_transfer", 0),
    ("phosphotransferase_system", 1)
], indirect=["model"])
def test_find_transport_reactions(model, num):
    """Expect amount of transporters to be identified correctly."""
    assert len(helpers.find_transport_reactions(model)) == num


@pytest.mark.parametrize("gpr_str, expected", [
    ("gene1 and gene2", [["gene1", "gene2"]]),
    ("gene1 or gene2", [["gene1"], ["gene2"]]),
    ("gene1 and (gene2 or gene3)", [["gene1", "gene2"], ["gene1", "gene3"]])
])
def test_find_functional_units(gpr_str, expected):
    """Expect type of enzyme complexes to be identified correctly."""
    assert list(helpers.find_functional_units(gpr_str)) == expected


@pytest.mark.parametrize("model, met_pair, expected", [
    ("converting_reactions", ("a", "b"), 2),
    ("converting_reactions", ("c", "c"), 1)
], indirect=["model"])
def test_find_converting_reactions(model, met_pair, expected):
    """Expect amount of converting reactions to be identified correctly."""
    assert len(helpers.find_converting_reactions(model, met_pair)) == expected
