# -*- coding: utf-8 -*-

# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
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

"""Perform basic tests on an instance of ``cobra.Model``."""

from __future__ import absolute_import

import memote.support.basic as basic


def test_model_id_presence(read_only_model, store):
    """Expect that the read_only_model has an ID."""
    assert hasattr(read_only_model, "id")
    store["model_id"] = read_only_model.id
    assert bool(read_only_model.id)


def test_genes_presence(read_only_model, store):
    """Expect that >= 1 genes are present in the read_only_model."""
    assert hasattr(read_only_model, "genes")
    store["num_genes"] = len(read_only_model.genes)
    assert len(read_only_model.genes) > 0


def test_reactions_presence(read_only_model, store):
    """Expect that >= 1 reactions are present in the read_only_model."""
    assert hasattr(read_only_model, "reactions")
    store["num_reactions"] = len(read_only_model.reactions)
    assert len(read_only_model.reactions) > 0


def test_metabolites_presence(read_only_model, store):
    """Expect that >= 1 metabolites are present in the read_only_model."""
    assert hasattr(read_only_model, "metabolites")
    store["num_metabolites"] = len(read_only_model.metabolites)
    assert len(read_only_model.metabolites) > 0


def test_metabolites_formula_presence(read_only_model, store):
    """Expect all metabolites to have a formula."""
    missing = [
        met.id for met in basic.check_metabolites_formula_presence(
            read_only_model
        )
    ]
    store["metabolites_no_formula"] = missing
    assert len(missing) == 0, "No formula found for the following "\
        "metabolites: {}".format(", ".join(missing))


def test_metabolites_charge_presence(read_only_model, store):
    """Expect all metabolites to have a formula."""
    missing = [
        met.id for met in basic.check_metabolites_charge_presence(
            read_only_model
        )
    ]
    store["metabolites_no_charge"] = missing
    assert len(missing) == 0, "No charge found for the following "\
        "metabolites: {}".format(", ".join(missing))


def test_gene_protein_reaction_rule_presence(read_only_model, store):
    """Expect all non-exchange reactions to have a GPR."""
    missing_gpr_metabolic_rxns = \
        set(
            basic.check_gene_protein_reaction_rule_presence(
                read_only_model
            )
        ).difference(set(read_only_model.exchanges))
    store["reactions_no_GPR"] = [rxn.id for rxn in missing_gpr_metabolic_rxns]
    assert len(store["reactions_no_GPR"]) == 0, "No GPR found for the " \
        "following reactions: {}".format(", ".join(missing_gpr_metabolic_rxns))


def test_ngam_presence(read_only_model, store):
    """Expect a single non growth-associated maintenance reaction."""
    ngam_reaction = basic.find_ngam(read_only_model)
    store["ngam_reaction"] = [rxn.id for rxn in ngam_reaction]
    assert len(ngam_reaction) == 1, \
        "Could not identify a unique non growth-associated maintenance " \
        "reaction. Please make sure to add only a single ATP-hydrolysis " \
        "reaction and set the lower bound to a fixed value."


def test_metabolic_coverage(read_only_model, store):
    """Expect a model to have high metabolic coverage."""
    store["metabolic_coverage"] = \
        basic.calculate_metabolic_coverage(read_only_model)
    assert store["metabolic_coverage"] >= 1
