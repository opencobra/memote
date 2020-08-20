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
    Return the maximum and minimum absolute, non-zero coefficients.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    s_matrix, _, _ = con_helpers.stoichiometry_matrix(
        model.metabolites, model.reactions
    )
    abs_matrix = np.abs(s_matrix)
    return abs_matrix.max(), abs_matrix[abs_matrix > 0].min()


def number_independent_conservation_relations(model):
    """
    Return the number of conserved metabolite pools.

    This number is given by the left null space of the stoichiometric matrix.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    s_matrix, _, _ = con_helpers.stoichiometry_matrix(
        model.metabolites, model.reactions
    )
    left_ns = con_helpers.nullspace(s_matrix.T)
    return left_ns.shape[1] if len(left_ns) > 1 else 0


def matrix_rank(model):
    """
    Return the rank of the model's stoichiometric matrix.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    s_matrix, _, _ = con_helpers.stoichiometry_matrix(
        model.metabolites, model.reactions
    )
    return con_helpers.rank(s_matrix)


def degrees_of_freedom(model):
    """
    Return the degrees of freedom, i.e., number of "free variables".

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    This specifically refers to the dimensionality of the (right) null space
    of the stoichiometric matrix, as dim(Null(S)) corresponds directly to the
    number of free variables in the system [1]_. The formula used calculates
    this using the rank-nullity theorem [2]_.

    References
    ----------
    .. [1] Fukuda, K. & Terlaky, T. Criss-cross methods: A fresh view on
       pivot algorithms. Mathematical Programming 79, 369-395 (1997).

    .. [2] Alama, J. The Rank+Nullity Theorem. Formalized Mathematics 15,
       (2007).

    """
    s_matrix, _, _ = con_helpers.stoichiometry_matrix(
        model.metabolites, model.reactions
    )
    return s_matrix.shape[1] - matrix_rank(model)
