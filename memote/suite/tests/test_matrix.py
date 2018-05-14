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


@annotate(title="Ratio between largest and smallest non-zero coefficients",
          format_type="percent")
def test_absolute_extreme_coefficient_ratio(model, threshold=1e9):
    """
    Show ratio of the absolute largest and smallest non-zero coefficients.

    This test will return the absolute largest and smallest, non-zero
    coefficients from the S-Matrix. A large ratio of these values may point to
    potential numerical issues when trying to solve the underlying system of
    equations.

    To pass this test the ratio should not exceed 10^9. This threshold has
    been selected based on experience, and is likely to be adapted when more
    data on solver performance becomes available.
    """
    ann = test_absolute_extreme_coefficient_ratio.annotation
    high, low = matrix.absolute_extreme_coefficient_ratio(model)
    ann["data"] = high / low
    # Inverse the Boolean: 0.0 = good; 1.0 = bad.
    ann["metric"] = 1.0 - float(ann["data"] < threshold)
    ann["message"] = wrapper.fill(
        """The ratio of the absolute values of the largest coefficient {} and
        the lowest, non-zero coefficient {} is: {:.3G}.""".format(
            high, low, ann["data"]))
    assert ann["data"] < threshold, ann["message"]


@annotate(title="Number of independent conservation relations in model",
          format_type="number")
def test_number_independent_conservation_relations(model):
    """
    Show number of independent conservation relations in the model.

    This test will return the number of conservation relations, i.e.
    conservation pools through the left null space of the S-Matrix.

    This test is not scored, as the dimension of the left null space
    depends on the S-Matrix constructed, which is system-specific.
    """
    ann = test_number_independent_conservation_relations.annotation
    ann["data"] = matrix.number_independent_conservation_relations(model)
    ann["message"] = wrapper.fill(
        """The number of independent conservation relations is {}.""".format(
            ann["data"]))


@annotate(title="Number of steady-state flux solution vectors",
          format_type="number")
def test_number_steady_state_flux_solutions(model):
    """
    Show number of independent steady-state flux solution vectors for model.

    This test will return the number of steady-state flux solution vectors
    through the null space of the S-Matrix.

    This test is not scored, as the dimension of the null space depends on the
    S-Matrix constructed, which is system-specific.
    """
    ann = test_number_steady_state_flux_solutions.annotation
    ann["data"] = matrix.number_steady_state_flux_solutions(model)
    ann["message"] = wrapper.fill(
        """The number of independent steady-state flux solution vectors is {}.
        """.format(ann["data"]))


@annotate(title="Rank of S-Matrix", format_type="number")
def test_matrix_rank(model):
    """
    Show rank of the S-Matrix.

    This test will return the rank of the S-Matrix of the model.

    This test is not scored, as the rank depends on the S-Matrix constructed,
    which is system-specific.
    """
    ann = test_matrix_rank.annotation
    ann["data"] = matrix.matrix_rank(model)
    ann["message"] = wrapper.fill(
        """The rank of the S-Matrix is {}.""".format(ann["data"]))


@annotate(title="Degrees of freedom of S-Matrix", format_type="number")
def test_degrees_of_freedom(model):
    """
    Show degrees of freedom of the S-Matrix.

    This test will return the degrees of freedom, i.e. "free variables" of the
    S-Matrix.

    This test is not scored, as the degrees of freedom depends on S-Matrix
    constructed, which is system-specific.
    """
    ann = test_degrees_of_freedom.annotation
    ann["data"] = matrix.degrees_of_freedom(model)
    ann["message"] = wrapper.fill(
        """The degrees of freedom of the S-Matrix is {}.""".format(
            ann["data"]))
