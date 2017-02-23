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

from __future__ import absolute_import

from ..support.basic import check_metabolites_formula_presence


"""
Basic tests performed on an instance of `cobra.Model`.
"""


def test_model_id_presence(model):
    """Expect that the model has an ID."""
    assert hasattr(model, "id")
    assert bool(model.id)


def test_metabolites_presence(model):
    """Expect that >= 1 metabolites are present in the model."""
    assert hasattr(model, "metabolites")
    assert len(model.metabolites) > 0


def test_reactions_presence(model):
    """Expect that >= 1 reactions are present in the model."""
    assert hasattr(model, "reactions")
    assert len(model.reactions) > 0


def test_metabolites_formula_presence(model):
    """Expect all metabolites to have a formula."""
    missing = check_metabolites_formula_presence(model)
    assert len(missing) == 0, "No formula found for the following "\
        "metabolites: {}".format(", ".join([met.id for met in missing]))
