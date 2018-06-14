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

"""
Perform tests on an instance of `cobra.Model` using growth data.

Growth data comes from processed biolog experiments. Growth curves have to be
converted into binary decisions whether or not an organism/strain was able to
grow in a certain medium.
"""

from __future__ import absolute_import

import pytest

from memote.utils import annotate, wrapper
from memote.support.essentiality import confusion_matrix

GROWTH_DATA = list(pytest.memote.experimental.growth)


@pytest.mark.skipif(len(GROWTH_DATA) == 0,
                    reason="No growth data found.")
@pytest.mark.parametrize("experiment", GROWTH_DATA)
@annotate(title="Growth Prediction", format_type="number",
          data=dict(), message=dict(), metric=dict())
def test_growth_from_data_qualitative(model, experiment, threshold=0.8):
    """
    Expect a perfect Matthew's coefficient.

    The in-silico growth prediction is compared with experimental
    data and the Matthew's coefficient is used as a metric.
    """
    ann = test_growth_from_data_qualitative.annotation
    exp = pytest.memote.experimental.growth[experiment]
    expected = exp.data
    test = exp.evaluate(model)
    # Growth data sets need not use unique exchange reactions thus we use the
    # numeric index here to compute the confusion matrix.
    ann["data"][experiment] = confusion_matrix(
        set(test.loc[test["growth"], "exchange"].index),
        set(expected.loc[expected["growth"], "exchange"].index),
        set(test.loc[~test["growth"], "exchange"].index),
        set(expected.loc[~expected["growth"], "exchange"].index)
    )
    ann["metric"][experiment] = ann["data"][experiment]["MCC"]
    ann["message"][experiment] = wrapper.fill(
        """Ideally, every model would show a perfect Matthews correlation
        coefficient of 1. In experiment '{}' the model has a coefficient
        of {:.2}.""".format(experiment, ann["data"][experiment]["MCC"])
    )
    assert ann["data"][experiment]["MCC"] > threshold
