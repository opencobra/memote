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
    if name == 'met_each_present':
        met = cobra.Metabolite(id='met_c', name="Met")
        met.annotation = {'metanetx.chemical': "MNXM23",
                          'kegg.compound': "C00022",
                          'seed.compound': "cpd00020",
                          'inchikey': "LCTONWCANYUPML-UHFFFAOYSA-M",
                          'chebi': ["CHEBI:14987", "CHEBI:15361",
                                    "CHEBI:26462", "CHEBI:26466",
                                    "CHEBI:32816", "CHEBI:45253",
                                    "CHEBI:86354", "CHEBI:8685"],
                          'hmdb': "HMDB00243",
                          'biocyc': "META:PYRUVATE",
                          'reactome': ["R-ALL-113557",
                                       "R-ALL-29398",
                                       "R-ALL-389680"],
                          'bigg.metabolite': "pyr"}
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.add_metabolites({met: -1})
        model.add_reactions([rxn])
        return model
    if name == 'met_each_absent':
        met = cobra.Metabolite(id='met_c', name="Met")
        met.annotation = {'METANETX': "MNXM23",
                          'old_database': "broken_identifier"}
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.add_metabolites({met: -1})
        model.add_reactions([rxn])
        return model
    if name == 'rxn_each_present':
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.annotation = {'metanetx.reaction': "MNXR13125",
                          'kegg.reaction': "R01068",
                          'ec-code': "4.1.2.13",
                          'brenda': "4.1.2.13",
                          'rhea': ["14729", "14730", "14731", "14732"],
                          'biocyc': "ECOLI:F16ALDOLASE-RXN",
                          'bigg.reaction': "FBA"}
        model.add_reactions([rxn])
        return model
    if name == 'rxn_each_absent':
        # Old or unknown databases and
        # keys that don't follow the MIRIAM namespaces
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.annotation = {'old_database': "broken_identifier",
                          'KEGG': "R01068"}
        model.add_reactions([rxn])
        return model
    if name == 'met_broken_id':
        met = cobra.Metabolite(id='met_c', name="Met")
        met.annotation = {'metanetx.chemical': "MNXR23",
                          'kegg.compound': "K00022",
                          'seed.compound': "cdp00020",
                          'inchikey': "LCT-ONWCANYUPML-UHFFFAOYSA-M",
                          'chebi': ["CHEBI:487", "CHEBI:15361",
                                    "CHEBI:26462", "CHEBI:26466",
                                    "CHEBI:32816", "CEBI:O",
                                    "CHEBI:86354", "CHEBI:8685"],
                          'hmdb': "HMBD00243",
                          'biocyc': "-PYRUVATE",
                          'reactome': ["113557", "29398", "389680"],
                          'bigg.metabolite': ":324RSF"}
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.add_metabolites({met: -1})
        model.add_reactions([rxn])
        return model
    if name == 'rxn_broken_id':
        rxn = cobra.Reaction(id='RXN', name="Rxn")
        rxn.annotation = {'metanetx.reaction': "MNXM13125",
                          'kegg.reaction': "T1068",
                          'ec-code': "4.1.2..13",
                          'brenda': "4.1.2..13",
                          'rhea': ["1472999", "14730", "14731", "ABCD"],
                          'biocyc': ":ECOLI_F16ALDOLASE-RXN",
                          'bigg.reaction': "/:2x_FBA"}
        model.add_reactions([rxn])
        return model


@pytest.mark.parametrize("model, num", [
    ("no_annotations", 2),
    ("met_annotations", 0)
], indirect=["model"])
def test_mets_without_annotation(model, num):
    """Expect all mets to have a non-empty annotation attribute"""
    mets_without_annotation = annotation.find_met_without_annotations(model)
    assert len(mets_without_annotation) == num


@pytest.mark.parametrize("model, num", [
    ("no_annotations", 1),
    ("rxn_annotations", 0)
], indirect=["model"])
def test_rxns_without_annotation(model, num):
    """Expect all rxns to have a non-empty annotation attribute"""
    rxns_without_annotation = annotation.find_rxn_without_annotations(model)
    assert len(rxns_without_annotation) == num


@pytest.mark.parametrize("model, num", [
    ("met_each_present", 0),
    ("met_each_absent", 1)
], indirect=["model"])
def test_mets_annotation_overview(model, num):
    """
    Expect all mets to have annotations from common databases.

    The required databases are outlined in annotation.py.
    """
    met_annotation_overview = \
        annotation.generate_met_annotation_overview(model)
    for key in annotation.METABOLITE_ANNOTATIONS:
        assert len(met_annotation_overview[key]) == num


@pytest.mark.parametrize("model, num", [
    ("rxn_each_present", 0),
    ("rxn_each_absent", 1)
], indirect=["model"])
def test_rxns_annotation_overview(model, num):
    """
    Expect all rxns to have annotations from common databases.

    The required databases are outlined in annotation.py.
    """
    rxn_annotation_overview = \
        annotation.generate_rxn_annotation_overview(model)
    for key in annotation.REACTION_ANNOTATIONS:
        assert len(rxn_annotation_overview[key]) == num


@pytest.mark.parametrize("model, num, rxn_or_met", [
    ("met_each_present", 0, "met"),
    ("met_broken_id", 1, "met"),
    ("rxn_each_present", 0, "rxn"),
    ("rxn_broken_id", 1, "rxn")
], indirect=["model"])
def test_find_wrong_annotation_ids(model, num, rxn_or_met):
    """
    Expect all items to have annotations that match MIRIAM patterns.

    The required databases and their patterns are outlined in annotation.py.
    """
    if rxn_or_met == "met":
        item_annotation_overview = \
            annotation.generate_met_annotation_overview(model)
    if rxn_or_met == "rxn":
        item_annotation_overview = \
            annotation.generate_rxn_annotation_overview(model)
    wrong_annotation_ids = annotation.find_wrong_annotation_ids(
        model,
        item_annotation_overview,
        rxn_or_met
    )
    for key in wrong_annotation_ids:
        assert len(wrong_annotation_ids[key]) == num
