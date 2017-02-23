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

from six import iteritems



def model_builder(name):
    model = cobra.Model(id_or_model=name, name=name)
    if name == "correct_tags":
        for i, pairs in enumerate(iteritems(syntax._SUFFIX_MAP)):
            if 'c' in pairs[0]:
                rxn = cobra.Reaction('R{}'.format(i))
            else:
                rxn = cobra.Reaction('R{}{}'.format(i, pairs[1]))
            rxn.add_metabolites(
                {cobra.Metabolite(id="M{0:d}_{1:s}".format(i, pairs[0])): -1,
                 cobra.Metabolite(id="B{0:d}_{1:s}".format(i, pairs[0])): 1}
            )
            model.add_reaction(rxn)
        return model

    if name == "no_tags":
        for i, pairs in enumerate(iteritems(syntax._SUFFIX_MAP)):
            rxn = cobra.Reaction('R{}'.format(i))
            rxn.add_metabolites(
                {cobra.Metabolite(id="M{0:d}_{1:s}".format(i, pairs[0])): -1,
                 cobra.Metabolite(id="B{0:d}_{1:s}".format(i, pairs[0])): 1}
            )
            model.add_reaction(rxn)
        return model

    if name == "wrong_tags":
        for i, pairs in enumerate(iteritems(syntax._SUFFIX_MAP)):
            rxn = cobra.Reaction('R{}tr'.format(i))
            rxn.add_metabolites(
                {cobra.Metabolite(id="M{0:d}_{1:s}".format(i, pairs[0])): -1,
                 cobra.Metabolite(id="B{0:d}_{1:s}".format(i, pairs[0])): 1}
            )
            model.add_reaction(rxn)
        return model


@pytest.mark.parametrize("model, num", [
    ("correct_tags", 0),
    ("no_tags", 1),
    ("wrong_tags", 1)
], indirect=["model"])
def test_non_transp_rxn_id_compartment_suffix_match(model, num):
    for compartment in model.compartments:
        if compartment != 'c':
            rxn_lst = syntax.find_reaction_tag_transporter(model, compartment)
            assert len (rxn_lst) == num
