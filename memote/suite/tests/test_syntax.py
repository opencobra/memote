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

"""Syntax tests performed on an instance of ``cobra.Model``."""

from __future__ import absolute_import

import pytest

import memote.support.syntax as syntax


@pytest.fixture(scope="module")
def non_cytosolic(read_only_model, store):
    """Provide all non-cytosolic compartments."""
    compartments = sorted(read_only_model.compartments)
    compartments.remove('c')
    store["non_cytosolic"] = compartments
    return compartments


def test_non_transp_rxn_id_compartment_suffix_match(read_only_model, store,
                                                    non_cytosolic):
    """Expect all reactions outside of the cytosol to be tagged accordingly."""
    store["reaction_compartment_suffix"] = list()
    for compartment in non_cytosolic:
        store["reaction_compartment_suffix"].append([
            rxn.id for rxn in syntax.find_rxn_id_compartment_suffix(
                read_only_model, compartment)])
    for compartment, no_match_rxns in zip(non_cytosolic,
                                          store["reaction_compartment_suffix"]):
        assert len(no_match_rxns) == 0, \
            "The following reactions in compartment {} are not tagged " \
            "correctly: {}".format(compartment, ", ".join(no_match_rxns))


def test_non_transp_rxn_id_suffix_compartment_match(
        read_only_model, store, non_cytosolic):
    """Expect compartment-tagged reactions to involve fitting metabolites."""
    store["reaction_metabolite_compartment"] = list()
    for compartment in non_cytosolic:
        store["reaction_metabolite_compartment"].append([
            rxn.id for rxn in syntax.find_rxn_id_suffix_compartment(
                read_only_model, compartment)])
    for compartment, mislab_rxns in zip(
            non_cytosolic, store["reaction_metabolite_compartment"]):
        assert len(mislab_rxns) == 0, \
            "The following reactions in compartment {} are tagged to not " \
            "contain metabolites from that compartment: {}"\
            "".format(compartment, ", ".join(mislab_rxns))


def test_non_abc_transp_rxn_tag_match(read_only_model, store):
    """Expect all non-abc transport reactions to be tagged with a ``t``."""
    store["untagged_normal_transport"] = [
        rxn.id for rxn in syntax.find_reaction_tag_transporter(
            read_only_model
        )]
    assert len(store["untagged_normal_transport"]) == 0, \
        "The following non-atp transport reactions are not tagged " \
        "correctly: {}".format(", ".join(store["untagged_normal_transport"]))


def test_abc_transp_rxn_tag_match(read_only_model, store):
    """Expect all abc transport reactions to be tagged with ``abc``."""
    store["untagged_abc_transport"] = [
        rxn.id for rxn in syntax.find_abc_tag_transporter(read_only_model)]
    assert len(store["untagged_abc_transport"]) == 0, \
        "The following abc transport reactions are not tagged" \
        "correctly: {}".format(", ".join(store["untagged_abc_transport"]))


def test_upper_case_mets(read_only_model, store):
    """Expect all metabolites to be lower case with accepted exceptions."""
    store["uppercase_metabolites"] = [
        met.id for met in syntax.find_upper_case_mets(read_only_model)]
    assert len(store["uppercase_metabolites"]) == 0, \
        "The IDs of the following metabolites are not written in lower case" \
        " {}".format(", ".join(store["uppercase_metabolites"]))


def test_demand_reaction_tag_match(read_only_model, store):
    """Expect all demand reaction IDs to be prefixed with ``DM_``."""
    store["untagged_demand"] = [
        rxn.id for rxn in syntax.find_untagged_demand_rxns(read_only_model)]
    assert len(store["untagged_demand"]) == 0, \
        "The IDs of the following demand reactions are not tagged with 'DM_'" \
        " {}".format(", ".join(store["untagged_demand"]))


def test_false_demand_reaction(read_only_model, store):
    """Expect all rxns that are tagged with ``DM_`` to be true demand rxns."""
    store["false_demand"] = [
        rxn.id for rxn in syntax.find_false_demand_rxns(read_only_model)]
    assert len(store["false_demand"]) == 0, \
        "The IDs of the following reactions are falsely tagged with 'DM_'" \
        " {}".format(", ".join(store["false_demand"]))


def test_sink_reaction_tag_match(read_only_model, store):
    """Expect all sink reaction IDs to be prefixed with ``SK_``."""
    store["untagged_sink"] = [
        rxn.id for rxn in syntax.find_untagged_sink_rxns(read_only_model)]
    assert len(store["untagged_sink"]) == 0, \
        "The IDs of the following sink reactions are not tagged with 'SK_'" \
        " {}".format(", ".join(store["untagged_demand"]))


def test_false_sink_reaction(read_only_model, store):
    """Expect all rxns that are tagged with ``SK_`` to be true sink rxns."""
    store["false_sink"] = [
        rxn.id for rxn in syntax.find_false_sink_rxns(read_only_model)]
    assert len(store["false_sink"]) == 0, \
        "The IDs of the following reactions are falsely tagged with 'SK_'" \
        " {}".format(", ".join(store["false_sink"]))


def test_exchange_reaction_tag_match(read_only_model, store):
    """Expect all exchange reaction IDs to be prefixed with ``EX_``."""
    store["untagged_exchange"] = [
        rxn.id for rxn in syntax.find_untagged_exchange_rxns(read_only_model)]
    assert len(store["untagged_exchange"]) == 0, \
        "The IDs of the following demand reactions are not tagged with 'EX_'" \
        " {}".format(", ".join(store["untagged_exchange"]))


def test_false_exchange_reaction(read_only_model, store):
    """Expect all rxns that are tagged with ``EX_`` to be true exchange rxns."""
    store["false_exchange"] = [
        rxn.id for rxn in syntax.find_false_exchange_rxns(read_only_model)]
    assert len(store["false_exchange"]) == 0, \
        "The IDs of the following reactions are falsely tagged with 'EX_'" \
        " {}".format(", ".join(store["false_exchange"]))
