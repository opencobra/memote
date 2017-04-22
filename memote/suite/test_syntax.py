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

"""Syntax tests performed on an instance of `cobra.Model`."""

from __future__ import absolute_import

from memote.support.syntax import (
    find_reaction_tag_transporter, find_rxn_id_compartment_suffix,
    find_abc_tag_transporter, find_upper_case_mets,
    find_rxn_id_suffix_compartment, find_untagged_demand_rxns,
    find_untagged_exchange_rxns
)


def test_non_transp_rxn_id_compartment_suffix_match(model):
    """Expect all reactions outside of the cytosol to be tagged accordingly."""
    for compartment in model.compartments:
        if compartment != 'c':
            no_match_rxns = find_rxn_id_compartment_suffix(model, compartment)
            assert \
                len(no_match_rxns) == 0, \
                "The following reactions in compartment {} are not tagged" \
                "correctly: {}".format(compartment,
                                       ", ".join(
                                           [rxn.id for rxn in no_match_rxns]
                                       )
                                       )


def test_non_transp_rxn_id_suffix_compartment_match(model):
    """
    Expect all rxns that are tagged to be in a compartment to at least
    partially involve mets from that compartment
    """
    for compartment in model.compartments:
        if compartment != 'c':
            mislab_rxns = find_rxn_id_suffix_compartment(model, compartment)
            assert \
                len(mislab_rxns) == 0, \
                "The following reactions in compartment {} are tagged to" \
                "don not contain metabolites from that " \
                "compartment: {}".format(compartment, ", ".join(
                                         [rxn.id for rxn in mislab_rxns]
                                         )
                                         )


def test_non_abc_transp_rxn_tag_match(model):
    """Expect all non-abc transport reactions to be tagged with a 't'."""
    untagged_non_atp_transport_rxns = find_reaction_tag_transporter(model)
    assert len(untagged_non_atp_transport_rxns) == 0, \
        "The following non-atp transport reactions are not tagged" \
        "correctly: {}".format(
        ", ".join([rxn.id for rxn in untagged_non_atp_transport_rxns]))


def test_abc_transp_rxn_tag_match(model):
    """Expect all abc transport rxns to be tagged with 'abc'"""
    untagged_atp_transport_rxns = find_abc_tag_transporter(model)
    assert len(untagged_atp_transport_rxns) == 0, \
        "The following abc transport reactions are not tagged" \
        "correctly: {}".format(
        ", ".join([rxn.id for rxn in untagged_atp_transport_rxns]))


def test_upper_case_mets(model):
    """Expect all metabolites to be lower case within accepted exceptions"""
    upper_case_mets = find_upper_case_mets(model)
    assert len(upper_case_mets) == 0, \
        "The IDs of the following metabolites are not written in lower case" \
        " {}".format(
        ", ".join([met.id for met in upper_case_mets]))


def test_demand_reaction_tag_match(model):
    """Expect all demand rxns IDs to be prefixed with 'DM_'"""
    falsely_tagged_demand_rxns = find_untagged_demand_rxns(model)
    assert len(falsely_tagged_demand_rxns) == 0, \
        "The IDs of the following demand reactions are not tagged with 'DM_'" \
        " {}".format(
        ", ".join([rxn.id for rxn in falsely_tagged_demand_rxns]))


def test_exchange_reaction_tag_match(model):
    """Expect all exchange rxns IDs to be prefixed with 'EX_'"""
    falsely_tagged_exchange_rxns = find_untagged_exchange_rxns(model)
    assert len(falsely_tagged_exchange_rxns) == 0, \
        "The IDs of the following demand reactions are not tagged with 'EX_'" \
        " {}".format(
        ", ".join([rxn.id for rxn in falsely_tagged_exchange_rxns]))
