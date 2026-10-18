# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Ensure that the SBO presence tests judge annotated and unannotated models."""

from __future__ import absolute_import

import pytest

import memote.support.helpers as helpers
from memote.suite import api


PRESENCE_TESTS = [
    # The demand and sink tests skip on e_coli_core, which has no such reactions.
    "test_metabolite_sbo_presence",
    "test_reaction_sbo_presence",
    "test_gene_sbo_presence",
    "test_metabolic_reaction_specific_sbo_presence",
    "test_transport_reaction_specific_sbo_presence",
    "test_metabolite_specific_sbo_presence",
    "test_gene_specific_sbo_presence",
    "test_exchange_specific_sbo_presence",
    "test_biomass_specific_sbo_presence",
]


def strip_sbo_terms(model):
    for component in model.metabolites + model.reactions + model.genes:
        component.annotation.pop("sbo", None)
    return model


def add_sbo_terms(model):
    for met in model.metabolites:
        met.annotation["sbo"] = "SBO:0000247"
    for gene in model.genes:
        gene.annotation["sbo"] = "SBO:0000243"
    exchanges = set(helpers.find_exchange_rxns(model))
    transports = set(helpers.find_transport_reactions(model))
    biomass = set(helpers.find_biomass_reaction(model))
    for rxn in model.reactions:
        if rxn in exchanges:
            rxn.annotation["sbo"] = "SBO:0000627"
        elif rxn in biomass:
            rxn.annotation["sbo"] = "SBO:0000629"
        elif rxn in transports:
            rxn.annotation["sbo"] = "SBO:0000185"
        else:
            rxn.annotation["sbo"] = "SBO:0000176"
    return model


@pytest.mark.parametrize(
    "model, annotate, outcome",
    [
        ("textbook", strip_sbo_terms, "failed"),
        ("textbook", add_sbo_terms, "passed"),
    ],
    indirect=["model"],
)
def test_sbo_presence_outcome(model, annotate, outcome):
    """The presence tests fail without SBO terms and pass with them (#777)."""
    _, results = api.test_model(
        annotate(model),
        results=True,
        exclusive=PRESENCE_TESTS,
        pytest_args=["--tb", "no", "-p", "no:cacheprovider"],
    )
    assert {name: results["tests"][name]["result"] for name in PRESENCE_TESTS} == {
        name: outcome for name in PRESENCE_TESTS
    }
