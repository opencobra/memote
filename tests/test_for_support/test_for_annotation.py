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

import memote.support.annotation as annotation

"""
Tests ensuring that the functions in `memote.support.annotation` work as
expected.
"""


def model_builder(name):
    """Returns a cobra.model built to reflect the required test case"""
    model = cobra.Model(id_or_model=name, name=name)
    if name == 'no_annotations':
        met = cobra.Metabolite(id='met_c', name="Met")
        met1 = cobra.Metabolite(id='met1_c', name="Met1")
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.add_metabolites({met: -1, met1: 1})
        model.add_reactions([rxn])
        return model
    if name == 'met_annotations':
        met = cobra.Metabolite(id='met_c', name="Met")
        met1 = cobra.Metabolite(id='met1_c', name="Met1")
        met.annotation = {'metanetx.chemical': 'MNXM1235'}
        met1.annotation = {'ec-code': '1.1.2.3'}
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.add_metabolites({met: -1, met1: 1})
        model.add_reactions([rxn])
        return model
    if name == 'rxn_annotations':
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.annotation = {'brenda': '1.1.1.1'}
        model.add_reactions([rxn])
        return model


@pytest.mark.parametrize("model, num", [
    ("no_annotations", 0),
    ("met_annotations", 2)
], indirect=["model"])
def test_mets_without_annotation(model, num):
    """Expect all mets to have a non-empty annotation attribute"""
    mets_without_annotation = annotation.find_met_without_annotations(model)
    assert len(mets_without_annotation) == num


@pytest.mark.parametrize("model, num", [
    ("no_annotations", 0),
    ("rxn_annotations", 1)
], indirect=["model"])
def test_rxns_without_annotation(model, num):
    """Expect all rxns to have a non-empty annotation attribute"""
    rxns_without_annotation = annotation.find_rxn_without_annotations(model)
    assert len(rxns_without_annotation) == num
