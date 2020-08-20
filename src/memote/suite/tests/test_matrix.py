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

"""Tests for matrix properties performed on an instance of ``cobra.Model``."""

from __future__ import absolute_import, division

import memote.support.matrix as matrix
from memote.utils import annotate, wrapper


@annotate(title="Ratio Min/Max Non-Zero Coefficients", format_type="percent")
def test_absolute_extreme_coefficient_ratio(model, threshold=1e9):
    """
    Show the ratio of the absolute largest and smallest non-zero coefficients.

    This test will return the absolute largest and smallest, non-zero
    coefficients of the stoichiometric matrix. A large ratio of these values
    may point to potential numerical issues when trying to solve different
    mathematical optimization problems such as flux-balance analysis.

    To pass this test the ratio should not exceed 10^9. This threshold has
    been selected based on experience, and is likely to be adapted when more
    data on solver performance becomes available.

    Implementation:
    Compose the stoichiometric matrix, then calculate absolute coefficients and
    lastly use the maximal value and minimal non-zero value to calculate the
    ratio.

    """
    ann = test_absolute_extreme_coefficient_ratio.annotation
    high, low = matrix.absolute_extreme_coefficient_ratio(model)
    ann["data"] = high / low
    # Inverse the Boolean: 0.0 = good; 1.0 = bad.
    ann["metric"] = 1.0 - float(ann["data"] < threshold)
    ann["message"] = wrapper.fill(
        """The ratio of the absolute values of the largest coefficient {} and
        the lowest, non-zero coefficient {} is: {:.3G}.""".format(
            high, low, ann["data"]
        )
    )
    assert ann["data"] < threshold, ann["message"]


@annotate(title="Independent Conservation Relations", format_type="raw")
def test_number_independent_conservation_relations(model):
    """
    Show the number of independent conservation relations in the model.

    This test will return the number of conservation relations, i.e.,
    conservation pools through the left null space of the stoichiometric
    matrix. This test is not scored, as the dimension of the left null space
    is system-specific.

    Implementation:
    Calculate the left null space, i.e., the null space of the transposed
    stoichiometric matrix, using an algorithm based on the singular value
    decomposition adapted from
    https://scipy.github.io/old-wiki/pages/Cookbook/RankNullspace.html
    Then, return the estimated dimension of that null space.

    """
    ann = test_number_independent_conservation_relations.annotation
    ann["data"] = matrix.number_independent_conservation_relations(model)
    # Report the number of ICR scaled by the number of metabolites.
    ann["metric"] = ann["data"] / len(model.metabolites)
    ann["message"] = wrapper.fill(
        """The number of independent conservation relations is {}.""".format(
            ann["data"]
        )
    )


@annotate(title="Rank", format_type="raw")
def test_matrix_rank(model):
    """
    Show the rank of the stoichiometric matrix.

    The rank of the stoichiometric matrix is system specific. It is
    calculated using singular value decomposition (SVD).

    Implementation:
    Compose the stoichiometric matrix, then estimate the rank, i.e. the
    dimension of the column space, of a matrix. The algorithm used by this
    function is based on the singular value decomposition of the matrix.

    """
    ann = test_matrix_rank.annotation
    ann["data"] = matrix.matrix_rank(model)
    # Report the rank scaled by the number of reactions.
    ann["metric"] = ann["data"] / len(model.reactions)
    ann["message"] = wrapper.fill(
        """The rank of the S-Matrix is {}.""".format(ann["data"])
    )


@annotate(title="Degrees Of Freedom", format_type="raw")
def test_degrees_of_freedom(model):
    """
    Show the degrees of freedom of the stoichiometric matrix.

    The degrees of freedom of the stoichiometric matrix, i.e., the number
    of 'free variables' is system specific and corresponds to the dimension
    of the (right) null space of the matrix.

    Implementation:
    Compose the stoichiometric matrix, then calculate the dimensionality of the
    null space using the rank-nullity theorem outlined by
    Alama, J. The Rank+Nullity Theorem. Formalized Mathematics 15, (2007).

    """
    ann = test_degrees_of_freedom.annotation
    ann["data"] = matrix.degrees_of_freedom(model)
    # Report the degrees of freedom scaled by the number of reactions.
    ann["metric"] = ann["data"] / len(model.reactions)
    ann["message"] = wrapper.fill(
        """The degrees of freedom of the S-Matrix are {}.""".format(ann["data"])
    )
