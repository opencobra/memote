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

"""Supporting functions for biomass consistency checks."""

from __future__ import absolute_import

import logging

from six import iteritems

__all__ = ("sum_biomass_weight",)

LOGGER = logging.getLogger(__name__)


def sum_biomass_weight(rxn):
    """Compute the sum of all reaction compounds."""
    return sum(-coef * met.formula_weight
               for (met, coef) in iteritems(rxn.metabolites)) / 1000.0
