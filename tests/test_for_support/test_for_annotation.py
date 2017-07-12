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


def no_annotations(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    met1 = cobra.Metabolite(id='met1_c', name="Met1")
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1, met1: 1})
    base.add_reactions([rxn])
    return base


def met_annotations(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    met1 = cobra.Metabolite(id='met1_c', name="Met1")
    met.annotation = {'metanetx.chemical': 'MNXM1235'}
    met1.annotation = {'ec-code': '1.1.2.3'}
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1, met1: 1})
    base.add_reactions([rxn])
    return base


def rxn_annotations(base):
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.annotation = {'brenda': '1.1.1.1'}
    base.add_reactions([rxn])
    return base


def met_each_present(base):
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
    base.add_reactions([rxn])
    return base


def met_each_absent(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    met.annotation = {'METANETX': "MNXM23",
                      'old_database': "broken_identifier"}
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1})
    base.add_reactions([rxn])
    return base


def rxn_each_present(base):
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.annotation = {'metanetx.reaction': "MNXR13125",
                      'kegg.reaction': "R01068",
                      'ec-code': "4.1.2.13",
                      'brenda': "4.1.2.13",
                      'rhea': ["14729", "14730", "14731", "14732"],
                      'biocyc': "ECOLI:F16ALDOLASE-RXN",
                      'bigg.reaction': "FBA"}
    base.add_reactions([rxn])
    return base


def rxn_each_absent(base):
    # Old or unknown databases and
    # keys that don't follow the MIRIAM namespaces
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.annotation = {'old_database': "broken_identifier",
                      'KEGG': "R01068"}
    base.add_reactions([rxn])
    return base


def met_broken_id(base):
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
                      'biocyc': "/:PYRUVATE",
                      'reactome': ["113557", "29398", "389680"],
                      'bigg.metabolite': ""}
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1})
    base.add_reactions([rxn])
    return base


def rxn_broken_id(base):
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.annotation = {'metanetx.reaction': "MNXM13125",
                      'kegg.reaction': "T1068",
                      'ec-code': "4.1.2..13",
                      'brenda': "4.1.2..13",
                      'rhea': ["1472999", "14730", "14731", "ABCD"],
                      'biocyc': ":ECOLI_F16ALDOLASE-RXN",
                      'bigg.reaction': "/:2x_FBA"}
    base.add_reactions([rxn])
    return base


def consistent_ids(base):
    met = cobra.Metabolite(id='pyr_c', name="Pyruvate")
    met1 = cobra.Metabolite(id='pep_c', name="Phosphoenolpyruvate")
    met2 = cobra.Metabolite(id='oaa_c', name="Oxaloacetate")
    rxn = cobra.Reaction(id='PYK', name="Pyruvate kinase")
    rxn.add_metabolites({met: -1, met1: 1})
    rxn2 = cobra.Reaction(id='PPC', name="Phosphoenolpyruvate carboxylase")
    rxn2.add_metabolites({met1: -1, met2: 1})
    rxn3 = cobra.Reaction(id='OAADC', name="Oxaloacetate decarboxylase")
    rxn3.add_metabolites({met2: -1, met: 1})
    base.add_reactions([rxn, rxn2, rxn3])
    return base


def inconsistent_ids(base):
    met = cobra.Metabolite(id='META:PYRUVATE_c', name="Pyruvate")
    met1 = cobra.Metabolite(id='pep_c', name="Phosphoenolpyruvate")
    met2 = cobra.Metabolite(id='oaa_c', name="Oxaloacetate")
    rxn = cobra.Reaction(id='PYK', name="Pyruvate kinase")
    rxn.add_metabolites({met: -1, met1: 1})
    rxn2 = cobra.Reaction(id='PPC', name="Phosphoenolpyruvate carboxylase")
    rxn2.add_metabolites({met1: -1, met2: 1})
    rxn3 = cobra.Reaction(id='4.1.1.3', name="Oxaloacetate decarboxylase")
    rxn3.add_metabolites({met2: -1, met: 1})
    base.add_reactions([rxn, rxn2, rxn3])
    return base


def model_builder(name):
    choices = {
        'no_annotations': no_annotations,
        'met_annotations': met_annotations,
        'rxn_annotations': rxn_annotations,
        'met_each_present': met_each_present,
        'met_each_absent': met_each_absent,
        'rxn_each_present': rxn_each_present,
        'rxn_each_absent': rxn_each_absent,
        'met_broken_id': met_broken_id,
        'rxn_broken_id': rxn_broken_id,
        'consistent_ids': consistent_ids,
        'inconsistent_ids': inconsistent_ids,
    }
    model = cobra.Model(id_or_model=name, name=name)
    return choices[name](model)


@pytest.mark.parametrize("model, num, components", [
    ("no_annotations", 2, "metabolites"),
    ("met_annotations", 0, "metabolites"),
    ("no_annotations", 1, "reactions"),
    ("rxn_annotations", 0, "reactions")
], indirect=["model"])
def test_find_components_without_annotation(model, num, components):
    """Expect `num` components to have no annotation."""
    without_annotation = annotation.find_components_without_annotation(
        model, components)
    assert len(without_annotation) == num


@pytest.mark.parametrize("model, num, components", [
    ("met_each_present", 1, "metabolites"),
    ("met_each_absent", 0, "metabolites"),
    ("rxn_each_present", 1, "reactions"),
    ("rxn_each_absent", 0, "reactions")
], indirect=["model"])
def test_generate_component_annotation_overview(model, num, components):
    """
    Expect all components to have `num` annotations from common databases.

    The required databases are outlined in `annotation.py`.
    """
    overview = \
        annotation.generate_component_annotation_overview(model, components)
    for key in overview.columns:
        assert overview[key].sum() == num


@pytest.mark.parametrize("model, num, components", [
    ("met_each_present", 1, "metabolites"),
    ("met_broken_id", 0, "metabolites"),
    ("rxn_each_present", 1, "reactions"),
    ("rxn_broken_id", 0, "reactions")
], indirect=["model"])
def test_generate_component_annotation_miriam_match(
        model, num, components):
    """
    Expect all items to have annotations that match MIRIAM patterns.

    The required databases are outlined in `annotation.py`.
    """
    annotation_matches = annotation.generate_component_annotation_miriam_match(
        model, components)
    for key in annotation_matches.columns:
        assert annotation_matches[key].sum() == num


@pytest.mark.parametrize("model, namespace, num, components", [
    ("consistent_ids", "bigg.metabolite", 3, "metabolites"),
    ("inconsistent_ids", "bigg.metabolite", 2, "metabolites"),
    ("consistent_ids", "bigg.reaction", 3, "reactions"),
    ("inconsistent_ids", "bigg.reaction", 2, "reactions")
], indirect=["model"])
def test_generate_component_id_namespace_overview(model, namespace, num,
                                                  components):
    """Expect `num` component IDs to be from the same namespace."""
    overview = annotation.generate_component_id_namespace_overview(
        model, components)
    distribution = overview.sum()
    assert distribution[namespace] == num
