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

"""Stoichiometric consistency tests for an instance of ``cobra.Model``."""

from __future__ import absolute_import

import memote.support.consistency as consistency


def test_stoichiometric_consistency(read_only_model, store):
    """Expect that the stoichiometry is mass-balanced."""
    is_consistent = consistency.check_stoichiometric_consistency(
        read_only_model)
    store["is_consistent"] = is_consistent
    unconserved = [] if is_consistent else [
        met.id for met in consistency.find_unconserved_metabolites(
            read_only_model)]
    store["unconserved_metabolites"] = unconserved
    assert is_consistent,\
        "The following metabolites are involved in inconsistent reactions:"\
        " {}".format(", ".join(unconserved))


def test_production_of_atp_closed_bounds(read_only_model, store):
    """Expect that ATP cannot be produced when all the bounds are closed."""
    store["magic_atp_production"] = consistency.produce_atp_closed_exchanges(
        read_only_model)
    assert not store["magic_atp_production"],\
        "Model can produce ATP with closed exchanges. This might be caused by"\
        " imbalanced reactions or loops."


def test_imbalanced_reactions(read_only_model, store):
    """Expect all reactions to be mass and charge balanced."""
    store["imbalanced_reactions"] = [
        rxn.id for rxn in consistency.find_imbalanced_reactions(
            read_only_model)]
    assert len(store["imbalanced_reactions"]) == 0,\
        "The following reactions are imbalanced: {}".format(
        ", ".join(store["imbalanced_reactions"]))


def test_blocked_reactions(read_only_model, store):
    """Expect all reactions to be able to carry flux."""
    store["blocked_reactions"] = [
        rxn.id for rxn in consistency.find_blocked_reactions(read_only_model)]
    assert len(store["blocked_reactions"]) == 0,\
        "The following reactions are blocked: {}".format(
            ", ".join(store["blocked_reactions"]))


def test_find_stoichiometrically_balanced_cycles(read_only_model, store):
    """Expect no stoichiometrically balanced loops to be present."""
    store["looped_reactions"] = [
        rxn.id for rxn in consistency.find_stoichiometrically_balanced_cycles(
            read_only_model
        )]
    assert len(store["looped_reactions"]) == 0,\
        "The following reactions participate in stoichiometrically balanced" \
        " cycles: {}".format(
            ", ".join(store["looped_reactions"]))
