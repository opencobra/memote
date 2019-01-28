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

"""Ensure the expected functioning of ``memote.support.annotation``."""

from __future__ import absolute_import

from builtins import dict

import cobra
import pytest

import memote.support.sbo as sbo
from memote.utils import register_with

MODEL_REGISTRY = dict()


@register_with(MODEL_REGISTRY)
def no_annotations(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    met1 = cobra.Metabolite(id='met1_c', name="Met1")
    met1.annotation = {'bigg.metabolite': 'dad_2'}
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1, met1: 1})
    rxn.gene_reaction_rule = '(gene1)'
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def specific_sbo_term(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    met.annotation = {'sbo': 'SBO:1', 'bigg.metabolite': 'dad_2'}
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1})
    rxn.annotation = {'bigg.reaction': 'DADNt2pp'}
    rxn.gene_reaction_rule = '(gene1)'
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def multiple_sbo_terms(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    met.annotation = {'sbo': ['SBO:1', 'SBO:2'],
                    'bigg.metabolite': 'dad_2'}
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1})
    rxn.annotation = {'bigg.reaction': 'DADNt2pp'}
    rxn.gene_reaction_rule = '(gene1)'
    base.add_reactions([rxn])
    return base


@register_with(MODEL_REGISTRY)
def biomass_sbo_term(base):
    met = cobra.Metabolite(id='met_c', name="Met")
    rxn = cobra.Reaction(id='RXN', name="Rxn")
    rxn.add_metabolites({met: -1})
    rxn.annotation = {'sbo': 'SBO:0000629'}
    base.add_reactions([rxn])
    return base


@pytest.mark.parametrize("model, num, components", [
    ("no_annotations", 2, "metabolites"),
    ("no_annotations", 1, "reactions"),
    ("no_annotations", 1, "genes")
], indirect=["model"])
def test_find_components_without_sbo_terms(model, num, components):
    """Expect `num` components to have no sbo annotation."""
    without_annotation = sbo.find_components_without_sbo_terms(
        model, components)
    assert len(without_annotation) == num


@pytest.mark.parametrize("model, num, components, term", [
    ("specific_sbo_term", 0, "metabolites", "SBO:1"),
    ("specific_sbo_term", 1, "reactions", "SBO:1"),
    ("specific_sbo_term", 1, "genes", "SBO:1"),
    ("biomass_sbo_term", 0, "reactions", "SBO:0000629"),
    ("multiple_sbo_terms", 0, "metabolites", ["SBO:1","SBO:2","SBO:3"]),
    ("multiple_sbo_terms", 1, "reactions", ["SBO:1","SBO:2","SBO:3"]),
    ("multiple_sbo_terms", 1, "genes", ["SBO:1","SBO:2","SBO:3"])
], indirect=["model"])
def test_find_components_without_specific_sbo_term(model, num, components,
                                                   term):
    """Expect `num` components to have a specific sbo annotation."""
    no_match_to_specific_term = sbo.check_component_for_specific_sbo_term(
        getattr(model, components), term)
    assert len(no_match_to_specific_term) == num
