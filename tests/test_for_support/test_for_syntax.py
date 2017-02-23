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

from __future__ import absolute_import

import cobra
import pytest

import memote.support.syntax as syntax


"""
Tests ensuring that the functions in `memote.support.syntax` work as expected.
"""


def model_builder(name):
    model = cobra.Model(id_or_model=name, name=name)
    if name == "rxn_correct_tags":
        for i, pairs in enumerate(syntax.SUFFIX_MAP.items()):
            if 'c' in pairs[0]:
                rxn = cobra.Reaction('R{}'.format(i))
            else:
                rxn = cobra.Reaction('R{}{}'.format(i, pairs[1]))
            rxn.add_metabolites(
                {cobra.Metabolite(id="M{0:d}_{1:s}".format(i, pairs[0]),
                                  compartment=pairs[0]): -1,
                 cobra.Metabolite(id="B{0:d}_{1:s}".format(i, pairs[0]),
                                  compartment=pairs[0]): 1}
            )
            model.add_reaction(rxn)
        return model

    if name == "rxn_no_tags":
        for i, pairs in enumerate(syntax.SUFFIX_MAP.items()):
            rxn = cobra.Reaction('R{}'.format(i))
            rxn.add_metabolites(
                {cobra.Metabolite(id="M{0:d}_{1:s}".format(i, pairs[0]),
                                  compartment=pairs[0]): -1,
                 cobra.Metabolite(id="B{0:d}_{1:s}".format(i, pairs[0]),
                                  compartment=pairs[0]): 1}
            )
            model.add_reaction(rxn)
        return model

    if name == "trxn_correct_tags":
        # Simple diffusion
        rxn = cobra.Reaction('Rt')
        rxn.add_metabolites(
            {cobra.Metabolite(id="M_m", formula='C6H12O6',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C6H12O6',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn)
        # Anti-Port
        rxn2 = cobra.Reaction('R2t')
        rxn2.add_metabolites(
            {cobra.Metabolite(id="D_c", formula='H',
                              compartment='c'): -1,
             cobra.Metabolite(id="D_m", formula='H',
                              compartment='m'): 1,
             cobra.Metabolite(id="M_m", formula='C6H12O6',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C6H12O6',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn2)
        # One-Metabolite transported
        rxn3 = cobra.Reaction('R3t')
        rxn3.add_metabolites(
            {cobra.Metabolite(id="D_c", formula='C21H26N7O14P2',
                              compartment='c'): -1,
             cobra.Metabolite(id="A_c", formula='C21H27N7O14P2',
                              compartment='c'): 1,
             cobra.Metabolite(id="C_c", formula='H',
                              compartment='c'): 1,
             cobra.Metabolite(id="M_m", formula='C6H12O6',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C6H12O6',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn3)
        return model

    if name == "trxn_no_tags":
        # Simple diffusion
        rxn = cobra.Reaction('R')
        rxn.add_metabolites(
            {cobra.Metabolite(id="M_m", formula='C6H12O6',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C6H12O6',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn)
        # Anti-Port
        rxn2 = cobra.Reaction('R2')
        rxn2.add_metabolites(
            {cobra.Metabolite(id="D_c", formula='H',
                              compartment='c'): -1,
             cobra.Metabolite(id="D_m", formula='H',
                              compartment='m'): 1,
             cobra.Metabolite(id="M_m", formula='C6H12O6',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C6H12O6',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn2)
        # One-Metabolite transported
        rxn3 = cobra.Reaction('R3')
        rxn3.add_metabolites(
            {cobra.Metabolite(id="D_c", formula='C21H26N7O14P2',
                              compartment='c'): -1,
             cobra.Metabolite(id="A_c", formula='C21H27N7O14P2',
                              compartment='c'): 1,
             cobra.Metabolite(id="C_c", formula='H',
                              compartment='c'): 1,
             cobra.Metabolite(id="M_m", formula='C6H12O6',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C6H12O6',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn3)
        return model

    if name == "trxn_correct_atp_driven":
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
             cobra.Metabolite(id="M_m", formula='C7H13NO2',
                              compartment='m'): -1,
             cobra.Metabolite(id="M_c", formula='C7H13NO2',
                              compartment='c'): 1}
        )
        model.add_reaction(rxn)
        return model

    if name == "proton_pump":
        # Proton pump
        rxn = cobra.Reaction('Rh')
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
        model.add_reaction(rxn)
        return model


@pytest.mark.parametrize("model, num", [
    ("rxn_correct_tags", 0),
    ("rxn_no_tags", 1)
], indirect=["model"])
def test_non_transp_rxn_id_compartment_suffix_match(model, num):
    for compartment in model.compartments:
        if compartment != 'c':
            rxn_lst = syntax.find_rxn_id_compartment_suffix(model, compartment)
            assert len(rxn_lst) == num


@pytest.mark.parametrize("model, num", [
    ("trxn_correct_tags", 0),
    ("trxn_correct_atp_driven", 0),
    ("trxn_no_tags", 3),
    ("proton_pump", 0)
], indirect=["model"])
def test_non_abc_transp_rxn_tag_match(model, num):
    trxn_lst = syntax.find_reaction_tag_transporter(model)
    assert len(trxn_lst) == num
