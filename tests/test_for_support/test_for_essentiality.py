# -*- coding: utf-8 -*-

# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Ensure the expected functioning of ``memote.support.essentiality``."""

from __future__ import absolute_import

import pytest
import numpy as np

import memote.support.essentiality as essentiality


@pytest.mark.parametrize("input_values, expected_results", [
    ([{"g1", "g2", "g3"}, {"g1", "g3"}, {"g4"}, {"g2", "g4"}], {
        "TP": ["g1", "g3"],
        "TN": ["g4"],
        "FP": ["g2"],
        "FN": [],
        "TPR": 1,
        "TNR": 0.5,
        "PPV": 0.6666666666666666,
        "FDR": 0.33333333333333337,
        "ACC": 0.75,
        "MCC": 0.5774
    })])
def test_confusion_matrix(input_values, expected_results):
    result_dict = essentiality.confusion_matrix(*input_values)
    for key, value in result_dict.items():
        if key in ['TPR', "TNR", "PPV", "FDR", "ACC", "MCC"]:
            assert np.isclose(value, expected_results[key], atol=1e-03)
        else:
            assert set(value) == set(expected_results[key])
