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

"""Supporting functions checking the matrix condition of the model object."""

from __future__ import absolute_import

import logging
import numpy as np
import memote.support.consistency_helpers as con_helpers

LOGGER = logging.getLogger(__name__)


def absolute_extreme_coefficient_ratio(model):
    """
    Return the absolute maximum and absolute non-zero minimum coefficients.
    """
    # S-Matrix with absolute values:
    s_matrix, _, _ = con_helpers.stoichiometry_matrix(
        model.metabolites, model.reactions
    )
    abs_matrix, _, _ = abs(s_matrix)

    absolute_max_coef = abs_matrix.max()
    absolute_non_zero_min_coef = np.min(abs_matrix[np.nonzero(abs_matrix)])

    return (absolute_max_coef, absolute_non_zero_min_coef)


def number_independent_conservation_relations(model):
    """
    Return the amount of conserved metabolic pools.
    """
    s_matrix, _, _ = con_helpers.stoichiometry_matrix(
        model.metabolites, model.reactions
    )
    n_matrix = con_helpers.nullspace(s_matrix)
    return n_matrix.shape[1]
