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

from ..support.syntax import check_rxn_id_compartment_suffix


def test_non_transp_rxn_id_compartment_suffix_match(model):
    """Expect all reactions outside of the cytosol to bear a tag accordingly"""
    for compartment in model.compartments:
        if compartment != 'c':
            assert \
                len(check_rxn_id_compartment_suffix(model, compartment)) == 0,\
                "Reactions in the following compartment are not tagged" \
                "correctly: {}".format(", ".join(compartment))
