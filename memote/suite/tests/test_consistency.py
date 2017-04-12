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

"""Supporting functions for stoichiometric consistency checks."""

from __future__ import absolute_import

import logging

from memote.support.consistency import (
    check_stoichiometric_consistency, find_unconserved_metabolites)

LOGGER = logging.getLogger(__name__)


def test_stoichiometric_consistency(model, store):
    """Expect that the metabolic model is mass-balanced."""
    is_consistent = check_stoichiometric_consistency(model)
    store["is_consistent"] = is_consistent
    unconserved = [] if is_consistent else\
        [met.id for met in find_unconserved_metabolites(model)]
    store["unconserved_metabolites"] = unconserved
    assert is_consistent,\
        "The following metabolites are involved in inconsistent reactions:"\
        " {}".format(", ".join(unconserved))


def test_production_of_atp_closed_bounds(model):
    """Expect that ATP cannot be produced when all the bounds are closed."""
    production_of_atp = consistency.produce_atp_closed_xchngs(model)
    assert production_of_atp is False,\
        "The model {} was able to produce ATP although all exchanges were"\
        "closed. This might be because there is an unbalanced reaction or a"\
        "loop in the model.".format(model.id)


def test_unbalanced_reactions(model):
    """Expect all reactions to be mass and charge balanced."""
    list_of_unbalanced_rxns = consistency.find_unbalanced_reactions(model)
    assert len(list_of_unbalanced_rxns) == 0, \
        "The following reactions are not balanced" \
        " {}".format(
        ", ".join([rxn.id for rxn in list_of_unbalanced_rxns]))
