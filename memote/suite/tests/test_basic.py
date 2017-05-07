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

"""Perform basic tests on an instance of `cobra.Model`."""

from __future__ import absolute_import

from memote.support.basic import check_metabolites_formula_presence


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
        met.id for met in check_metabolites_formula_presence(read_only_model)]
    store["num_metabolites_no_formula"] = missing
    assert len(missing) == 0, "No formula found for the following "\
        "metabolites: {}".format(", ".join(missing))
