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
Perform tests on an instance of `cobra.Model` using gene data.

Gene data currently only includes knockout screens. However, other types of
experiments that make changes to individual genes such as expression
modulation experiments, etc may be possible extensions in the future.
"""

from __future__ import absolute_import

import pytest

from memote.support.essentiality import confusion_matrix
from memote.utils import annotate, wrapper


@pytest.mark.essentiality
@annotate(
    title="Gene Essentiality Prediction",
    format_type="percent",
    data=dict(),
    message=dict(),
    metric=dict(),
)
def test_gene_essentiality_from_data_qualitative(model, experiment, threshold=0.95):
    """
    Expect a perfect accuracy when predicting gene essentiality.

    The in-silico gene essentiality is compared with experimental
    data and the accuracy is expected to be better than 0.95.
    In principal, Matthews' correlation coefficient is a more comprehensive
    metric but is a little fragile to not having any false negatives or false
    positives in the output.

    Implementation:
    Read and validate experimental config file and data tables. Constrain the
    model with the parameters provided by a user's definition of the medium,
    then compute a confusion matrix based on the predicted essential, expected
    essential, predicted nonessential and expected nonessential genes.
    The individual values of the confusion matrix are calculated as described
    in https://en.wikipedia.org/wiki/Confusion_matrix

    """
    ann = test_gene_essentiality_from_data_qualitative.annotation
    name, exp = experiment
    expected = exp.data
    test = exp.evaluate(model)
    ann["data"][name] = result = confusion_matrix(
        set(test.loc[test["essential"], "gene"]),
        set(expected.loc[expected["essential"], "gene"]),
        set(test.loc[~test["essential"], "gene"]),
        set(expected.loc[~expected["essential"], "gene"]),
    )
    ann["metric"][name] = result["ACC"]
    ann["message"][name] = wrapper.fill(
        """Ideally, every model would show a perfect accuracy of 1. In
        name '{}' the model has  {:.2}.""".format(
            name, result["ACC"]
        )
    )
    assert result["ACC"] > threshold
