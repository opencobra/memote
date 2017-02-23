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

"""
Syntax tests performed on an instance of `cobra.Model`.
"""

from ..support.syntax import (
    find_rxn_id_compartment_suffix,
    find_reaction_tag_transporter
)


def test_non_transp_rxn_id_compartment_suffix_match(model):
    """Expect all rxns outside of the cytosol to be tagged accordingly"""
    for compartment in model.compartments:
        if compartment != 'c':
            no_match_rxns = find_rxn_id_compartment_suffix(model, compartment)
            assert \
                len(no_match_rxns) == 0,\
                "The following reactions in compartment {} are not tagged" \
                "correctly: {}".format(compartment,
                                       ", ".join(
                                           [met.id for met in no_match_rxns]
                                            )
                                       )


def test_non_abc_transp_rxn_tag_match(model):
    """Expect all non-abc transport rxns to be tagged with a 't'"""
    untagged_non_atp_transport_rxns = find_reaction_tag_transporter(model)
    assert len(untagged_non_atp_transport_rxns) == 0,\
        "The following non-atp transport reactions are not tagged" \
        "correctly: {}".format(
            ", ".join(
                    [met.id for met in untagged_non_atp_transport_rxns]
            )
        )
