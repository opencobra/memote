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

"""Supporting functions for basic checks performed on the model object."""

from __future__ import absolute_import

import logging

__all__ = ("check_metabolites_formula_presence",)


LOGGER = logging.getLogger(__name__)


def check_metabolites_formula_presence(model):
    """Return the list of model metabolites that have no associated formula."""
    return [met for met in model.metabolites if not met.formula]


def check_metabolites_charge_presence(model):
    """Return the list of model metabolites that have no associated charge."""
    return [met for met in model.metabolites if not type(met.charge) == int]


def check_gene_protein_reaction_rule_presence(model):
    """Return the list of model reactions that have no associated gene rule."""
    return [rxn for rxn in model.reactions if not rxn.gene_reaction_rule]
