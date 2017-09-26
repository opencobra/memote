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

import pytest

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


@pytest.mark.parametrize(
    "read_only_model, store, met",
    [("read_only_model", "store", x) for x in consistency.ENERGY_COUPLES],
    indirect=["read_only_model", "store"])
def test_detect_energy_generating_cycles(read_only_model, store, met):
    """Expect that no energy metabolite can be produced out of nothing."""
    try:
        result = \
            consistency.detect_energy_generating_cycles(read_only_model, met)
    except KeyError as err:
        result = "not found"
    store["magic_{}_production".format(met)] = result

    if result == "not found":
        assert False,\
            "The metabolite '{}' was not found in the model.".format(met)
    elif result == "infeasible":
        assert False,\
            "Solving the model is infeasible. Often this is due to missing " \
            "or disconnected metabolites, or too strict constraints."
    else:
        assert len(result) == 0,\
            "The model can produce '{}' without requiring resources. This is " \
            "likely caused by improperly constrained reactions leading to " \
            "erroneous energy-generating cycles.".format(met)


def test_reaction_charge_balance(read_only_model, store):
    """Expect all reactions to be charge balanced."""
    store["charge_imbalanced_reactions"] = [
        rxn.id for rxn in consistency.find_charge_imbalanced_reactions(
            read_only_model)]
    assert len(store["charge_imbalanced_reactions"]) == 0,\
        "The following reactions are charge imbalanced or at least one " \
        "metabolite participating in a reaction doesn't have a charge" \
        ": {}".format(", ".join(store["charge_imbalanced_reactions"]))


def test_reaction_mass_balance(read_only_model, store):
    """Expect all reactions to be mass balanced."""
    store["mass_imbalanced_reactions"] = [
        rxn.id for rxn in consistency.find_mass_imbalanced_reactions(
            read_only_model)]
    assert len(store["mass_imbalanced_reactions"]) == 0,\
        "The following reactions are mass imbalanced or at least one " \
        "metabolite participating in a reaction doesn't have a formula" \
        ": {}".format(", ".join(store["mass_imbalanced_reactions"]))


def test_blocked_reactions(read_only_model, store):
    """Expect all reactions to be able to carry flux."""
    store["blocked_reactions"] = [
        rxn.id for rxn in consistency.find_blocked_reactions(read_only_model)]
    assert len(store["blocked_reactions"]) == 0,\
        "The following reactions are blocked: {}".format(
            ", ".join(store["blocked_reactions"]))


@pytest.mark.skip(reason="Loopless FVA currently runs too slow for large "
                         "models.")
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


def test_find_orphans(read_only_model, store):
    """Expect no orphans to be present."""
    store["orphan_metabolites"] = [
        met.id for met in consistency.find_orphans(read_only_model)]
    assert len(store["orphan_metabolites"]) == 0,\
        "The following metabolites are not produced by any " \
        "reaction of the model: {}".format(
            ", ".join(store["orphan_metabolites"]))


def test_find_deadends(read_only_model, store):
    """Expect no deadends to be present."""
    store["deadend_metabolites"] = [
        met.id for met in consistency.find_deadends(read_only_model)]
    assert len(store["deadend_metabolites"]) == 0,\
        "The following metabolites are not consumed by any " \
        "reaction of the model: {}".format(
            ", ".join(store["deadend_metabolites"]))


def test_find_disconnected(read_only_model, store):
    """Expect no disconnected metabolites to be present."""
    store["disconnected_metabolites"] = [
        met.id for met in consistency.find_disconnected(read_only_model)]
    assert len(store["disconnected_metabolites"]) == 0,\
        "The following metabolites are not associated with any " \
        "reaction of the model: {}".format(
            ", ".join(store["disconnected_metabolites"]))
