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

import numpy as np

from memote.support.biomass import sum_biomass_weight

from memote.support.helpers import find_biomass_reaction


def test_biomass_consistency(model):
    """
    Expect that the sum of total mass of all biomass components equals 1.

    Allow for an absolute tolerance of 1e-03.
    """
    biomass_rxns = find_biomass_reaction(model)
    for rxn in biomass_rxns:
        control_sum = sum_biomass_weight(rxn)
        assert np.isclose(1.0, control_sum, atol=1e-03), \
            "The following biomass reaction does not sum close enough to 1'" \
            " {}".format(
            ", ".join(rxn.id))
