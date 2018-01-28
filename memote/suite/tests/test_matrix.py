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
          type="percent"
)
def test_absolute_extreme_coefficient_ratio(model):
    """Show ratio of the absolute largest and smallest non-zero coefficients.

    This test will return the absolute largest and smallest, non-zero
    coefficients from the S-Matrix. A large ratio of these values may point to
    potential numerical issues when trying to solve the underlying system of
    equations.

    To pass this test the ratio should not exceed 10^9. This threshold has
    been selected based on experience, and is likely to be adapted when more
    data on solver performance becomes available.
    """
    ann = test_absolute_extreme_coefficient_ratio.annotation
    ann["data"] = matrix.absolute_extreme_coefficient_ratio(model)
    ann["metric"] = ann["data"][0] / ann["data"][1]
    ann["message"] = wrapper.fill(
        """The ratio of the absolute highest coefficient {} and the lowest,
        non-zero coefficient {} is: {}""".format(
            ann["data"][0], ann["data"][1], ann['metric']
        ))
    assert ann["metric"] < 1e9, ann["message"]
