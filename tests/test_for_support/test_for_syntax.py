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

"""Ensure the expected functioning of ``memote.support.syntax``."""

from __future__ import absolute_import

import cobra
import pytest

import memote.support.syntax as syntax
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def rxn_correct_tags(base):
    for i, pairs in enumerate(syntax.SUFFIX_MAP.items()):
        if 'c' in pairs[0]:
            rxn = cobra.Reaction('R{}'.format(i))
        else:
            rxn = cobra.Reaction('R{}{}'.format(i, pairs[1]))
        base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def rxn_no_tags(base):
    for i, pairs in enumerate(syntax.SUFFIX_MAP.items()):
        rxn = cobra.Reaction('R{}'.format(i))
        rxn.add_metabolites(
            {cobra.Metabolite(id="m{0:d}_{1:s}".format(i, pairs[0]),
                              compartment=pairs[0]): -1,
             cobra.Metabolite(id="b{0:d}_{1:s}".format(i, pairs[0]),
                              compartment=pairs[0]): 1}
        )
        base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def rxn_tags_but_wrong_compartments(base):
    misaligned_suffix_map = dict({'p': 'c',
                                  'c': 'e',
                                  'e': 'er',
                                  'er': 'g',
                                  'g': 'l',
                                  'l': 'm',
                                  'm': 'n',
                                  'n': 'x',
                                  'x': 'v',
                                  'v': 'pp'})

    for i, pairs in enumerate(misaligned_suffix_map.items()):
        rxn = cobra.Reaction('R{}{}'.format(i, pairs[1]))
        rxn.add_metabolites(
            {cobra.Metabolite(id="m{0:d}_{1:s}".format(i, pairs[0]),
                              compartment=pairs[0]): -1,
             cobra.Metabolite(id="b{0:d}_{1:s}".format(i, pairs[0]),
                              compartment=pairs[0]): 1}
        )
        base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def trxn_correct_tags(base):
    # Simple diffusion
    rxn = cobra.Reaction('Rt')
    rxn.add_metabolites(
        {cobra.Metabolite(id="m_m", formula='C6H12O6',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C6H12O6',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn)
    # Anti-Port
    rxn2 = cobra.Reaction('R2t')
    rxn2.add_metabolites(
        {cobra.Metabolite(id="d_c", formula='H',
                          compartment='c'): -1,
         cobra.Metabolite(id="d_m", formula='H',
                          compartment='m'): 1,
         cobra.Metabolite(id="m_m", formula='C6H12O6',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C6H12O6',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn2)
    # One-Metabolite transported
    rxn3 = cobra.Reaction('R3t')
    rxn3.add_metabolites(
        {cobra.Metabolite(id="d_c", formula='C21H26N7O14P2',
                          compartment='c'): -1,
         cobra.Metabolite(id="a_c", formula='C21H27N7O14P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="c_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C6H12O6',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C6H12O6',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn3)
    return base


@register_with(MODEL_REGISTRY)
def trxn_no_tags(base):
    # Simple diffusion
    rxn = cobra.Reaction('R')
    rxn.add_metabolites(
        {cobra.Metabolite(id="m_m", formula='C6H12O6',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C6H12O6',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn)
    # Anti-Port
    rxn2 = cobra.Reaction('R2')
    rxn2.add_metabolites(
        {cobra.Metabolite(id="d_c", formula='H',
                          compartment='c'): -1,
         cobra.Metabolite(id="d_m", formula='H',
                          compartment='m'): 1,
         cobra.Metabolite(id="m_m", formula='C6H12O6',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C6H12O6',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn2)
    # One-Metabolite transported
    rxn3 = cobra.Reaction('R3')
    rxn3.add_metabolites(
        {cobra.Metabolite(id="d_c", formula='C21H26N7O14P2',
                          compartment='c'): -1,
         cobra.Metabolite(id="a_c", formula='C21H27N7O14P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="c_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C6H12O6',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C6H12O6',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn3)
    return base


@register_with(MODEL_REGISTRY)
def trxn_correct_atp_driven(base):
    # ATP-driven
    rxn = cobra.Reaction('Rabc')
    rxn.add_metabolites(
        {cobra.Metabolite(id="atp_c", formula='C10H12N5O13P3',
                          compartment='c'): -1,
         cobra.Metabolite(id="adp_c", formula='C10H12N5O10P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="p_c", formula='HO4P',
                          compartment='c'): 1,
         cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C7H13NO2',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C7H13NO2',
                          compartment='c'): 1}
    )
    # GTP-driven
    rxn2 = cobra.Reaction('R2abc')
    rxn2.add_metabolites(
        {cobra.Metabolite(id="gtp_c", formula='C10H12N5O14P3',
                          compartment='c'): -1,
         cobra.Metabolite(id="gdp_c", formula='C10H12N5O11P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="p_c", formula='HO4P',
                          compartment='c'): 1,
         cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C7H13NO2',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C7H13NO2',
                          compartment='c'): 1}
    )
    # CTP-driven
    rxn3 = cobra.Reaction('R3abc')
    rxn3.add_metabolites(
        {cobra.Metabolite(id="ctp_c", formula='C9H12N3O14P3',
                          compartment='c'): -1,
         cobra.Metabolite(id="cdp_c", formula='C9H12N3O11P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="p_c", formula='HO4P',
                          compartment='c'): 1,
         cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C7H13NO2',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C7H13NO2',
                          compartment='c'): 1}
    )
    base.add_reactions([rxn, rxn2, rxn3])
    return base


@register_with(MODEL_REGISTRY)
def trxn_no_tag_atp_driven(base):
    # ATP-driven
    rxn = cobra.Reaction('R')
    rxn.add_metabolites(
        {cobra.Metabolite(id="atp_c", formula='C10H12N5O13P3',
                          compartment='c'): -1,
         cobra.Metabolite(id="adp_c", formula='C10H12N5O10P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="p_c", formula='HO4P',
                          compartment='c'): 1,
         cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C7H13NO2',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C7H13NO2',
                          compartment='c'): 1}
    )
    # GTP-driven
    rxn2 = cobra.Reaction('R2')
    rxn2.add_metabolites(
        {cobra.Metabolite(id="gtp_c", formula='C10H12N5O14P3',
                          compartment='c'): -1,
         cobra.Metabolite(id="gdp_c", formula='C10H12N5O11P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="p_c", formula='HO4P',
                          compartment='c'): 1,
         cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C7H13NO2',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C7H13NO2',
                          compartment='c'): 1}
    )
    # CTP-driven
    rxn3 = cobra.Reaction('R3')
    rxn3.add_metabolites(
        {cobra.Metabolite(id="ctp_c", formula='C9H12N3O14P3',
                          compartment='c'): -1,
         cobra.Metabolite(id="cdp_c", formula='C9H12N3O11P2',
                          compartment='c'): 1,
         cobra.Metabolite(id="p_c", formula='HO4P',
                          compartment='c'): 1,
         cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): 1,
         cobra.Metabolite(id="m_m", formula='C7H13NO2',
                          compartment='m'): -1,
         cobra.Metabolite(id="m_c", formula='C7H13NO2',
                          compartment='c'): 1}
    )
    base.add_reactions([rxn, rxn2, rxn3])
    return base


@register_with(MODEL_REGISTRY)
def proton_pump(base):
    # Proton pump
    rxn = cobra.Reaction('Ah')
    rxn.add_metabolites(
        {cobra.Metabolite(id="h_c", formula='H',
                          compartment='c'): -2,
         cobra.Metabolite(id="o2_c", formula='O2',
                          compartment='c'): -0.5,
         cobra.Metabolite(id="h_p", formula='H',
                          compartment='p'): 2,
         cobra.Metabolite(id="h2o_c", formula='HO2',
                          compartment='c'): 1}
    )
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def atp_synthase(base):
    # ATPS
    atp = cobra.Metabolite("atp_c", formula='C10H12N5O13P3', compartment="c")
    adp = cobra.Metabolite("adp_c", formula='C10H12N5O10P2', compartment="c")
    h_c = cobra.Metabolite("h_c", formula='H', compartment="c")
    pi = cobra.Metabolite("pi_c", formula='HO4P', compartment="c")
    h2o = cobra.Metabolite("h2o_c", formula='H2O', compartment="c")
    h_p = cobra.Metabolite("h_p", formula='H', compartment="p")
    atps = cobra.Reaction("ATPS")
    atps.add_metabolites({h_c: -4, adp: -1, pi: -1,
                          atp: 1, h2o: 1, h_p: 3})
    base.add_reactions([atps])
    return base


@register_with(MODEL_REGISTRY)
def lower_case_mets(base):
    rxn = cobra.Reaction('RLOM')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abcdeACP_c"): -1,
         cobra.Metabolite(id="fghij__L_c"): -1,
         cobra.Metabolite(id="klmnop_R_p"): 2,
         cobra.Metabolite(id="qrSt_uvw_E_c"): 1,
         cobra.Metabolite(id="xyZ123456789_c"): 1}
    )
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def upper_case_mets(base):
    rxn = cobra.Reaction('RHIM')
    rxn.add_metabolites(
        {cobra.Metabolite(id="AbcdeACP_c"): -1,
         cobra.Metabolite(id="fGHij__L_c"): -1,
         cobra.Metabolite(id="KLMNOP_R_p"): 2,
         cobra.Metabolite(id="QRSt_uvw_E_c"): 1,
         cobra.Metabolite(id="xYZ123456789_c"): 1}
    )
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def correct_demand_tag(base):
    rxn = cobra.Reaction('DM_abc_c')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_c",
                          compartment='c'): -1}
    )
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def missing_demand_tag(base):
    rxn = cobra.Reaction('EX_abc_c')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_c",
                          compartment='c'): -1}
    )
    rxn1 = cobra.Reaction('def_c')
    rxn1.add_metabolites(
        {cobra.Metabolite(id="def_c",
                          compartment='c'): -1}
    )
    base.add_reactions([rxn, rxn1])
    return base


@register_with(MODEL_REGISTRY)
def false_demand_tag(base):
    rxn = cobra.Reaction('DM_abc_e')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_e",
                          compartment='e'): -1}
    )
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def correct_exchange_tag(base):
    rxn = cobra.Reaction('EX_abc_e')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_e",
                          compartment='e'): -1}
    )
    base.add_reaction(rxn)
    return base


@register_with(MODEL_REGISTRY)
def missing_exchange_tag(base):
    rxn = cobra.Reaction('DM_ghi_e')
    rxn.add_metabolites(
        {cobra.Metabolite(id="ghi_e",
                          compartment='e'): -1}
    )
    rxn1 = cobra.Reaction('jkm_e')
    rxn1.add_metabolites(
        {cobra.Metabolite(id="jkm_e",
                          compartment='e'): -1}
    )
    base.add_reactions([rxn, rxn1])
    return base


@register_with(MODEL_REGISTRY)
def correct_sink_tag(base):
    rxn = cobra.Reaction('SK_abc_c')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_c",
                          compartment='c'): -1}
    )
    rxn.lower_bound = -1000
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def missing_sink_tag(base):
    rxn = cobra.Reaction('EX_abc_c')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_c",
                          compartment='c'): -1}
    )
    rxn.lower_bound = -1000
    rxn1 = cobra.Reaction('SINK_def_c')
    rxn1.add_metabolites(
        {cobra.Metabolite(id="def_c",
                          compartment='c'): -1}
    )
    rxn1.lower_bound = -1000
    base.add_reactions([rxn, rxn1])
    return base


@register_with(MODEL_REGISTRY)
def false_sink_tag(base):
    rxn = cobra.Reaction('SK_abc_c')
    rxn.add_metabolites(
        {cobra.Metabolite(id="abc_c",
                          compartment='c'): -1}
    )
    base.add_reactions([rxn])
    return base


@pytest.mark.parametrize("model, num", [
    ("rxn_correct_tags", 0),
    ("rxn_no_tags", 1)
], indirect=["model"])
def test_non_transp_rxn_id_compartment_suffix_match(model, num):
    """Expect all rxns outside of the cytosol to be tagged accordingly."""
    for compartment in model.compartments:
        if compartment != 'c':
            rxn_lst = syntax.find_rxn_id_compartment_suffix(model, compartment)
            assert len(rxn_lst) == num


@pytest.mark.parametrize("model, num", [
    ("rxn_correct_tags", 0),
    ("rxn_tags_but_wrong_compartments", 1)
], indirect=["model"])
def test_non_transp_rxn_id_suffix_compartment_match(model, num):
    """
    Expect all rxns that are tagged to be in a compartment to at least
    partially involve mets from that compartment.
    """
    for compartment in model.compartments:
        if compartment != 'c':
            mislab_rxns = syntax.find_rxn_id_suffix_compartment(
                model, compartment
            )
            assert \
                len(mislab_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("trxn_correct_tags", 0),
    ("trxn_correct_atp_driven", 0),
    ("trxn_no_tags", 3),
    ("proton_pump", 1),
    ("atp_synthase", 0)
], indirect=["model"])
def test_non_abc_transp_rxn_tag_match(model, num):
    """Expect all non-abc transport rxns to be tagged with a 't'."""
    trxn_lst = syntax.find_reaction_tag_transporter(model)
    assert len(trxn_lst) == num


@pytest.mark.parametrize("model, num", [
    ("trxn_correct_atp_driven", 0),
    ("trxn_no_tag_atp_driven", 3)
], indirect=["model"])
def test_abc_transp_rxn_tag_match(model, num):
    """Expect all abc transport rxns to be tagged with 'abc'."""
    untagged_atp_transport_rxns = syntax.find_abc_tag_transporter(model)
    assert len(untagged_atp_transport_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("lower_case_mets", 0),
    ("upper_case_mets", 5)
], indirect=["model"])
def test_upper_case_mets(model, num):
    """Expect all metabolites to be lower case within accepted exceptions."""
    upper_case_mets = syntax.find_upper_case_mets(model)
    assert len(upper_case_mets) == num


@pytest.mark.parametrize("model, num", [
    ("correct_demand_tag", 0),
    ("missing_demand_tag", 2)
], indirect=["model"])
def test_demand_reaction_tag_match(model, num):
    """Expect all demand rxn IDs to be prefixed with 'DM_'."""
    untagged_tagged_demand_rxns = syntax.find_untagged_demand_rxns(model)
    assert len(untagged_tagged_demand_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("correct_demand_tag", 0),
    ("false_demand_tag", 1),
    ("missing_exchange_tag", 1)
], indirect=["model"])
def test_false_demand_reaction(model, num):
    """Expect all rxns that are tagged with 'DM_' to be true demand rxns."""
    falsely_tagged_demand_rxns = syntax.find_false_demand_rxns(model)
    assert len(falsely_tagged_demand_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("correct_sink_tag", 0),
    ("missing_sink_tag", 2)
], indirect=["model"])
def test_sink_reaction_tag_match(model, num):
    """Expect all sink rxn IDs to be prefixed with 'SK_'."""
    untagged_tagged_sink_rxns = syntax.find_untagged_sink_rxns(model)
    assert len(untagged_tagged_sink_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("correct_sink_tag", 0),
    ("false_sink_tag", 1)
], indirect=["model"])
def test_false_sink_reaction(model, num):
    """Expect all rxns that are tagged with 'SK_' to be true sink rxns."""
    falsely_tagged_sink_rxns = syntax.find_false_sink_rxns(model)
    assert len(falsely_tagged_sink_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("correct_exchange_tag", 0),
    ("missing_exchange_tag", 2)
], indirect=["model"])
def test_exchange_reaction_tag_match(model, num):
    """Expect all exchange rxn IDs to be prefixed with 'EX_'."""
    untagged_tagged_exchange_rxns = syntax.find_untagged_exchange_rxns(model)
    assert len(untagged_tagged_exchange_rxns) == num


@pytest.mark.parametrize("model, num", [
    ("correct_exchange_tag", 0),
    ("missing_demand_tag", 1)
], indirect=["model"])
def test_false_exchange_reaction(model, num):
    """Expect all rxns that are tagged with 'EX_' to be true exchange rxns."""
    falsely_tagged_exchange_rxns = syntax.find_false_exchange_rxns(model)
    assert len(falsely_tagged_exchange_rxns) == num
