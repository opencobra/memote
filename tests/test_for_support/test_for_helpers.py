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
REACTION_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def uni_anti_symport_formulae(base):
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
def uni_anti_symport_annotations(base):
    """Provide a model with 3 simple transport reactions."""
    met_a = cobra.Metabolite("co2_c", compartment="c")
    met_b = cobra.Metabolite("co2_e", compartment="e")
    met_c = cobra.Metabolite("na_c", compartment="c")
    met_d = cobra.Metabolite("na_e", compartment="e")

    met_a.annotation["bigg.metabolite"] = "co2"
    met_b.annotation["bigg.metabolite"] = "co2"
    met_c.annotation["bigg.metabolite"] = "na1"
    met_d.annotation["bigg.metabolite"] = "na1"

    uni = cobra.Reaction("UNI")
    uni.add_metabolites({met_a: 1, met_b: -1})
    anti = cobra.Reaction("ANTI")
    anti.add_metabolites({met_a: 1, met_d: 1, met_b: -1, met_c: -1})
    sym = cobra.Reaction("SYM")
    sym.add_metabolites({met_a: 1, met_c: 1, met_b: -1, met_d: -1})
    base.add_reactions([uni, anti, sym])
    return base


@register_with(MODEL_REGISTRY)
def abc_pump_formulae(base):
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
def abc_pump_annotations(base):
    """Provide a model with an ABC transport reaction."""
    atp = cobra.Metabolite("atp_c", compartment="c")
    adp = cobra.Metabolite("adp_c", compartment="c")
    h = cobra.Metabolite("h_c", compartment="c")
    pi = cobra.Metabolite("pi_c", compartment="c")
    h2o = cobra.Metabolite("h2o_c", compartment="c")
    aso_c = cobra.Metabolite("aso3_c", compartment="c")
    aso_e = cobra.Metabolite("aso3_e", compartment="e")

    atp.annotation["biocyc"] = ["META:ATP", "META:CPD0-1634"]
    adp.annotation["biocyc"] = ["META:ADP", "META:CPD0-1651"]
    h.annotation["biocyc"] = "META:PROTON"
    pi.annotation["biocyc"] = ["META:CPD-16459", "META:CPD-9010"]
    h2o.annotation["biocyc"] = ["META:CPD-15815", "META:HYDROXYL-GROUP"]
    aso_c.annotation["biocyc"] = ["META:CPD0-2040", "META:CPD-763"]
    aso_e.annotation["biocyc"] = ["META:CPD0-2040", "META:CPD-763"]

    pump = cobra.Reaction("PUMP")
    pump.add_metabolites({aso_c: -1, atp: -1, h2o: -1,
                          adp: 1, h: 1, pi: 1, aso_e: 1})
    base.add_reactions([pump])
    return base


@register_with(MODEL_REGISTRY)
def proton_pump_formulae(base):
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
def proton_pump_annotations(base):
    """Provide a model with an ABC proton pump reaction."""
    atp = cobra.Metabolite("atp_c", formula='C10H12N5O13P3', compartment="c")
    adp = cobra.Metabolite("adp_c", formula='C10H12N5O10P2', compartment="c")
    h_c = cobra.Metabolite("h_c", formula='H', compartment="c")
    pi = cobra.Metabolite("pi_c", formula='HO4P', compartment="c")
    h2o = cobra.Metabolite("h2o_c", formula='H2O', compartment="c")
    h_p = cobra.Metabolite("h_p", formula='H', compartment="p")

    atp.annotation["biocyc"] = ["META:ATP", "META:CPD0-1634"]
    adp.annotation["biocyc"] = ["META:ADP", "META:CPD0-1651"]
    h_c.annotation["biocyc"] = "META:PROTON"
    pi.annotation["biocyc"] = ["META:CPD-16459", "META:CPD-9010"]
    h2o.annotation["biocyc"] = ["META:CPD-15815", "META:HYDROXYL-GROUP"]
    h_p.annotation["biocyc"] = "META:PROTON"

    pump = cobra.Reaction("PUMP")
    pump.add_metabolites({h_c: -4, adp: -1, pi: -1,
                          atp: 1, h2o: 1, h_p: 3})
    base.add_reactions([pump])
    return base


@register_with(MODEL_REGISTRY)
def phosphotransferase_system_formulae(base):
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
def phosphotransferase_system_annotations(base):
    """Provide a model with a PTS transport reaction."""
    pep = cobra.Metabolite("pep_c", compartment="c")
    pyr = cobra.Metabolite("pyr_c", compartment="c")
    malt = cobra.Metabolite(",malt_e", compartment="e")
    malt6p = cobra.Metabolite("malt6p_c", compartment="c")

    pep.annotation["biocyc"] = "META:PHOSPHO-ENOL-PYRUVATE"
    pyr.annotation["biocyc"] = "META:PYRUVATE"
    malt.annotation["biocyc"] = ["META:ALPHA-MALTOSE", "META:MALTOSE"]
    malt6p.annotation["biocyc"] = ["META:CPD-1244", "META:CPD-15982"]

    pst = cobra.Reaction("PST")
    pst.add_metabolites({pep: -1, malt: -1, pyr: 1, malt6p: 1})
    base.add_reactions([pst])
    return base


@register_with(MODEL_REGISTRY)
def energy_transfer_formulae(base):
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
def energy_transfer_annotations(base):
    """Provide a model with a membrane-spanning electron transfer reaction."""
    cytaox = cobra.Metabolite("cytaox_c", compartment="c")
    cytared = cobra.Metabolite("cytared_c", compartment="c")
    cytbox = cobra.Metabolite("cytbox_m", compartment="m")
    cytbred = cobra.Metabolite("cytbred_m", compartment="m")
    cytaox.annotation["kegg.compound"] = "NAD"
    cytared.annotation["kegg.compound"] = "NADH"
    cytbox.annotation["kegg.compound"] = "UBIQUINONE-ox"
    cytbred.annotation["kegg.compound"] = "UBIQUINONE-red"
    et = cobra.Reaction("ET")
    et.add_metabolites({cytaox: -1, cytbred: -1, cytared: 1, cytbox: 1})
    base.add_reactions([et])
    return base


@register_with(MODEL_REGISTRY)
def labeled_reaction(base):
    """Provide a model with a labeled transport reaction."""
    a = cobra.Metabolite("a", compartment="c")
    b = cobra.Metabolite("b", compartment="p")
    rxn = cobra.Reaction("rxn")
    rxn.annotation["sbo"] = "SBO:0000655"
    rxn.add_metabolites({a: -1, b: 1})
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def unlabeled_reaction(base):
    """Provide a model with a labeled transport reaction."""
    a = cobra.Metabolite("a")
    b = cobra.Metabolite("b")
    rxn = cobra.Reaction("rxn")
    rxn.add_metabolites({a: -1, b: 1})
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def ndpk1_annotation(base):
    """Provide a model with a reportedly false positive."""
    a = cobra.Metabolite("atp_c", compartment="c")
    b = cobra.Metabolite("adp_c", compartment="c")
    c = cobra.Metabolite("gtp_c", compartment="c")
    d = cobra.Metabolite("gdp_c", compartment="c")
    b.charge = -3
    b.formula = "C10H12N5O10P2"
    b.annotation = {
        "chebi": "45626",
        "kegg.compound": "cpd00008",
        "biocyc": "ADP",
        "seed.compound": "cpd00008",
        "pubchem": "6022",
        "fc_source": "MetaCyc"
    }
    a.charge = -4
    a.formula = "C10H12N5O13P3"
    a.annotation = {
        "chebi": "30616",
        "kegg.compound": "C00002",
        "biocyc": "ATP",
        "seed.compound": "cpd00002",
        "pubchem": "5957",
        "fc_source": "MetaCyc"
    }
    c.charge = -4
    c.formula = "C10H12N5O14P3"
    c.annotation = {
        "chebi": "57600",
        "kegg.compound": "C00044",
        "biocyc": "GTP",
        "seed.compound": "cpd00038",
        "pubchem": "6830",
        "fc_source": "MetaCyc"
    }
    d.charge = -3
    d.formula = "C10H12N5O11P2"
    d.annotation = {
        "chebi": "58189",
        "kegg.compound": "C00035",
        "biocyc": "GDP",
        "seed.compound": "cpd00031",
        "pubchem": "8977",
        "fc_source": "MetaCyc"
    }
    rxn = cobra.Reaction("NDPK1")
    rxn.add_metabolites({a: -1, d: -1, b: 1, c: 1})
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def converting_reactions(base):
    """Provide a model with a couple of converting reaction."""
    a = cobra.Metabolite("atp_c", compartment="c")
    b = cobra.Metabolite("adp_c", compartment="c")
    c = cobra.Metabolite("gtp_c", compartment="c")
    c2 = cobra.Metabolite("gtp_e", compartment="e")
    c3 = cobra.Metabolite("gtp_p", compartment="p")
    rxn1 = cobra.Reaction("R1")
    rxn1.add_metabolites({a: -1, b: 1})
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({a: -1, c: -1, b: 1, c2: 1})
    rxn3 = cobra.Reaction("R3")
    rxn3.add_metabolites({a: -1, c3: 1, c2: 1})
    base.add_reactions([rxn1, rxn2, rxn3])
    return base


@register_with(MODEL_REGISTRY)
def one_exchange(base):
    rxn = cobra.Reaction('EX_abc_e')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_e",
                          compartment='e'): -1}
    )
    rxn.bounds = -1, 5
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def find_met_id(base):
    """
    Provide a model with existing metabolite IDs from different namespaces.
    """
    # ATP - BiGG ID
    a = cobra.Metabolite("atp_c", compartment='c')
    # GTP - Chebi ID
    b = cobra.Metabolite("15996", compartment='c')
    # CDP - Deprecated MetaNetX ID
    c = cobra.Metabolite("MNXM90125", compartment='c')
    # Asparagine - Kegg ID
    d = cobra.Metabolite("C00152", compartment='c')
    # Glycine - MetaCyc ID
    e = cobra.Metabolite("GLY", compartment='c')
    # Pyridoxal Phosphate - Current MetaNetX ID
    f = cobra.Metabolite("MNXM161", compartment='c')
    # Coenzyme A - Seed ID
    g = cobra.Metabolite("cpd00010", compartment='c')
    # ADP - Cryptic ID - MNX ID in the annotation
    h = cobra.Metabolite("OVER9000_c0", compartment='c')
    h.annotation = {"metanetx.chemical": "MNXM7"}
    # Proton - Cryptic ID - Chebi array in the annotation
    i = cobra.Metabolite("x12", compartment='c')
    i.annotation = {"chebi": ["15378", "10744", "13357", "5584",
                              "24636", "29233", "29234"]}
    base.add_metabolites([a, b, c, d, e, f, g, h, i])
    return base


@register_with(MODEL_REGISTRY)
def find_met_incorrect_xref(base):
    """
    Provide a model with metabolite IDs not in shortlist or wrong.
    """
    # Hydrogen - HMDB ID typo
    a = cobra.Metabolite("HMDB59598", compartment='c')
    # NADH and NAD - BiGG ID but
    b = cobra.Metabolite("nad_c", compartment='c')
    c = cobra.Metabolite("nad_e", compartment='c')
    base.add_metabolites([a, b, c])
    return base


@register_with(MODEL_REGISTRY)
def compartments1(base):
    """
    Provide a model with unconventional compartment names.
    """
    test_case = {'default': 'default',
                 'c_15': 'some unknown name'}
    base.add_metabolites([cobra.Metabolite('A', compartment='default')])
    base.compartments = test_case
    return base


@register_with(MODEL_REGISTRY)
def no_compartments(base):
    """
    Provide a model with no compartments.
    """
    base.add_metabolites([cobra.Metabolite('MNXM161')])
    return base


@register_with(MODEL_REGISTRY)
def compartment_size(base):
    """
    Provide a model with different amounts metabolites for each compartment.
    """
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='c') for i in "ABCD"])
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='e') for i in "EFG"])
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='p') for i in "HI"])
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='v') for i in "JK"])
    return base


@register_with(MODEL_REGISTRY)
def compartment_size_uncommon_keys(base):
    """
    Provide a model with different amounts metabolites for each compartment.
    """
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='ml') for i in "ABCD"])
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='om') for i in "EFG"])
    return base


@register_with(MODEL_REGISTRY)
def edge_case(base):
    """
    Provide an edge case where compartment detection fails.
    """
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='ml') for i in "ABC"])
    base.add_metabolites(
        [cobra.Metabolite(i, compartment='om') for i in "DEF"])
    return base


@register_with(MODEL_REGISTRY)
def biomass_buzzwords(base):
    """Provide a model with a reaction that will be identified as biomass."""
    a = cobra.Metabolite("Protein_c", compartment="c")
    b = cobra.Metabolite("DNA_c", compartment="c")
    c = cobra.Metabolite("RNA_c", compartment="c")
    d = cobra.Metabolite("GAM_c", compartment="c")
    rxn1 = cobra.Reaction("BOF", name='Biomass')
    rxn1.add_metabolites({a: -1, b: -1, c: -1, d: -1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
def biomass_sbo(base):
    """Provide a model with a reaction that will be identified as biomass."""
    a = cobra.Metabolite("Protein_c", compartment="c")
    b = cobra.Metabolite("DNA_c", compartment="c")
    c = cobra.Metabolite("RNA_c", compartment="c")
    d = cobra.Metabolite("GAM_c", compartment="c")
    rxn1 = cobra.Reaction("R0001")
    rxn1.annotation = {'sbo': 'SBO:0000629'}
    rxn1.add_metabolites({a: -1, b: -1, c: -1, d: -1})
    base.add_reactions([rxn1])
    return base


@register_with(MODEL_REGISTRY)
def biomass_metabolite(base):
    """Provide a model with a reaction that will be identified as biomass."""
    a = cobra.Metabolite("Protein_c", compartment="c")
    b = cobra.Metabolite("DNA_c", compartment="c")
    c = cobra.Metabolite("RNA_c", compartment="c")
    d = cobra.Metabolite("GAM_c", compartment="c")
    e = cobra.Metabolite("Biomass_c", compartment="c")
    rxn1 = cobra.Reaction("R0001")
    rxn1.add_metabolites({a: -1, b: -1, c: -1, d: -1, e: 1})
    rxn2 = cobra.Reaction("EX_Biomass")
    rxn2.add_metabolites({e: -1})
    base.add_reactions([rxn1, rxn2])
    return base


@register_with(REACTION_REGISTRY)
def transport_reaction_true():
    """Provide a transport reaction identifiable through met annotations"""
    a = cobra.Metabolite("X", compartment="c")
    a.annotation["bigg.metabolite"] = "co2"
    b = cobra.Metabolite("x", compartment="e")
    b.annotation["bigg.metabolite"] = "co2"
    r = cobra.Reaction("Transporter")
    r.add_metabolites({a: -1, b: 1})
    return r


@register_with(REACTION_REGISTRY)
def transport_reaction_missing_annotation():
    """Provide a transport reaction identifiable through met annotations"""
    a = cobra.Metabolite("X", compartment="c")
    b = cobra.Metabolite("x", compartment="e")
    r = cobra.Reaction("Transporter_Missing_Ann")
    r.add_metabolites({a: -1, b: 1})
    return r


@register_with(REACTION_REGISTRY)
def transport_reaction_missing_values():
    """Provide a transport reaction identifiable through met annotations"""
    a = cobra.Metabolite("X", compartment="c")
    a.annotation["bigg.metabolite"] = None
    b = cobra.Metabolite("x", compartment="e")
    b.annotation["bigg.metabolite"] = None
    r = cobra.Reaction("Transporter_Missing_Values")
    r.add_metabolites({a: -1, b: 1})
    return r


@register_with(REACTION_REGISTRY)
def transport_reaction_false():
    """Provide a fake transport reaction that uses SBO terms"""
    a = cobra.Metabolite("X", compartment="c")
    a.annotation["sbo"] = "SBO:00001"
    b = cobra.Metabolite("XH", compartment="c")
    b.annotation["sbo"] = "SBO:00001"
    c = cobra.Metabolite("DH", compartment="e")
    c.annotation["sbo"] = "SBO:00001"
    d = cobra.Metabolite("D", compartment="e")
    d.annotation["sbo"] = "SBO:00001"
    r = cobra.Reaction("ElectronTransfer")
    r.add_metabolites({a: -1, b: 1, c: -1, d: 1})
    return r


@pytest.mark.parametrize("model, num", [
    ("uni_anti_symport_formulae", 3),
    ("uni_anti_symport_annotations", 3),
    ("abc_pump_formulae", 1),
    ("abc_pump_annotations", 1),
    ("proton_pump_formulae", 1),
    ("proton_pump_annotations", 1),
    ("energy_transfer_formulae", 0),
    ("energy_transfer_annotations", 0),
    ("phosphotransferase_system_formulae", 1),
    ("phosphotransferase_system_annotations", 0),
    ("labeled_reaction", 1),
    ("unlabeled_reaction", 0),
    ("ndpk1_annotation", 0)
], indirect=["model"])
def test_find_transport_reactions(model, num):
    """Expect amount of transporters to be identified correctly."""
    assert len(helpers.find_transport_reactions(model)) == num


@pytest.mark.parametrize("model, met_pair, expected", [
    ("converting_reactions", ("MNXM3", "MNXM7"), 2),
    ("converting_reactions", ("MNXM51", "MNXM51"), 1)
], indirect=["model"])
def test_find_converting_reactions(model, met_pair, expected):
    """Expect amount of converting reactions to be identified correctly."""
    assert len(helpers.find_converting_reactions(model, met_pair)) == expected


@pytest.mark.parametrize("model, reaction_id, bounds", [
    ("one_exchange", "EX_abc_e", (-1000, 1000)),
], indirect=["model"])
def test_open_boundaries(model, reaction_id, bounds):
    """Expect amount of transporters to be identified correctly."""
    helpers.open_boundaries(model)
    assert model.reactions.get_by_id(reaction_id).bounds == bounds


@pytest.mark.parametrize("model, mnx_id, compartment_id, expected", [
    ("find_met_id", "MNXM3", "c", "atp_c"),
    ("find_met_id", "MNXM51", None, "15996"),
    ("find_met_id", "MNXM220", None, "MNXM90125"),
    ("find_met_id", "MNXM147", None, "C00152"),
    ("find_met_id", "MNXM29", None, "GLY"),
    ("find_met_id", "MNXM161", None, "MNXM161"),
    ("find_met_id", "MNXM12", None, "cpd00010"),
    ("find_met_id", "MNXM7", "c", "OVER9000_c0"),
    ("find_met_id", "MNXM1", "c", "x12"),
    ("no_compartments", "MNXM161", None, "MNXM161"),
], indirect=["model"])
def test_find_met_in_model_accurate_results(
    model, mnx_id, compartment_id, expected
):
    """Expect the metabolite represented by mnxid to be found correctly."""
    met = helpers.find_met_in_model(
        model, mnx_id, compartment_id=compartment_id
    )
    assert met[0].id == expected


@pytest.mark.parametrize("model, mnx_id, compartment_id", [
    pytest.param("find_met_incorrect_xref", "MNXM1", "c",
                 marks=pytest.mark.raises(exception=RuntimeError)),
    pytest.param("find_met_incorrect_xref", "MNXM13", None,
                 marks=pytest.mark.raises(exception=ValueError)),
    pytest.param("find_met_incorrect_xref", "MNXM13", "c",
                 marks=pytest.mark.raises(exception=ValueError)),
    pytest.param("find_met_incorrect_xref", "MNXM8", "c",
                 marks=pytest.mark.raises(exception=RuntimeError)),
], indirect=["model"])
def test_find_met_in_model_exceptions(model, mnx_id, compartment_id):
    """Expect the function to raise the correct exceptions."""
    helpers.find_met_in_model(model, mnx_id, compartment_id=compartment_id)


@pytest.mark.parametrize("model, compartment_id, expected", [
    ("compartments1", "c", "default"),
    ("compartment_size", "c", "c"),
    ("compartment_size_uncommon_keys", "c", "ml")
], indirect=["model"])
def test_find_compartment_id_in_model(model, compartment_id, expected):
    """Expect the compartment ID of the model to be found correctly."""
    comp_id = helpers.find_compartment_id_in_model(model, compartment_id)
    assert comp_id == expected


@pytest.mark.parametrize("model, compartment_id", [
    pytest.param("no_compartments", "c",
                 marks=pytest.mark.raises(exception=KeyError)),
    pytest.param("compartments1", "xx",
                 marks=pytest.mark.raises(exception=KeyError))
], indirect=["model"])
def test_find_compartment_id_in_model_exceptions(model, compartment_id):
    """Expect the compartment ID of the model to be found correctly."""
    helpers.find_compartment_id_in_model(model, compartment_id)


@pytest.mark.parametrize("model", [
    pytest.param("edge_case",
                 marks=pytest.mark.raises(exception=RuntimeError))
], indirect=["model"])
def test_largest_compartment_id_equal_sizes(model):
    """Expect the compartment ID of the model to be found correctly."""
    helpers.largest_compartment_id_met(model)


@pytest.mark.parametrize("model, compartment_id, count", [
    ("compartment_size", "c", 4),
    ("compartment_size", "h", 0)
], indirect=["model"])
def test_find_metabolites_per_compartment(model, compartment_id, count):
    """
    Expect the amount of metabolites per compartment to be counted correctly.
    """
    assert len(
        helpers.metabolites_per_compartment(model, compartment_id)
    ) == count


@pytest.mark.parametrize("model, expected", [
    ("compartment_size", "c")
], indirect=["model"])
def test_largest_compartment_id_met(model, expected):
    """
    Expect the ID of the compartment with most metabolites to be identified.
    """
    assert helpers.largest_compartment_id_met(model) == expected


@pytest.mark.parametrize("model, expected", [
    ("biomass_buzzwords", 1),
    ("biomass_sbo", 1),
    ("biomass_metabolite", 1),
], indirect=["model"])
def test_find_biomass_reaction(model, expected):
    """
    Expect the biomass reaction to be identified correctly.
    """
    assert len(helpers.find_biomass_reaction(model)) == expected


@pytest.mark.parametrize("reaction, boolean", [
    ("transport_reaction_true", True),
    ("transport_reaction_false", None),
    ("transport_reaction_missing_annotation", None),
    ("transport_reaction_missing_values", None)
], indirect=["reaction"])
def test_is_transport_reaction_annotations(reaction, boolean):
    """
    Expect the reaction to be identified as transport reaction by annotations.
    """
    assert helpers.is_transport_reaction_annotations(reaction) == boolean
