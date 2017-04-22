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
