# -*- coding: utf-8 -*-

# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability,
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
Tests ensuring that the functions in `memote.support.basic` work as expected.
"""

import pytest
import cobra

import memote.support.syntax as syntax


def model_builder(name):
    model = cobra.Model(id_or_model=name, name=name)
    return model


@pytest.mark.parametrize("model, num", [
    ("empty", 0),
], indirect=["model"])
def test_rxn_id_compartment_suffix(model, num, compartment_suffix):
    assert len(syntax.check_rxn_id_compartment_suffix(model, compartment_suffix)) == num
