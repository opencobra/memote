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

import memote.support.experimental.essentiality as genome


# CONFIG = ExperimentConfiguration.load(join("data", "experiments",
#  "essentiality.yml"))#
# if exists(CONFIG):#
#     with open(CONFIG) as file_h:#
#         CONFIG = yaml.safe_load(file_h)#
# else:#
#     CONFIG = None

EXPERIMENT_PATHS = []


@pytest.fixture(params=EXPERIMENT_PATHS)
def comparative_dataframe(request, read_only_model):
    """Provide single dataframe with experimental and predicted results."""
    if hasattr(request, "param"):
        return genome.prepare_essentiality_data(request.param, read_only_model)


def test_gene_essentiality_from_data_qualitative(comparative_dataframe, store):
    """Expect the amount of true positives to equal the amount ot genes."""
    if comparative_dataframe is None:
        pytest.xfail("No data found.")
    comparative_dataframe, exp = \
        genome.prepare_qualitative_comparison(comparative_dataframe)
    store['qualitative_essentiality_dataframe_{}'.format(exp[:-11])] \
        = comparative_dataframe
    store['qualitative_true_positives_{}'.format(exp[:-11])] = len(
        comparative_dataframe[comparative_dataframe["true_positives"] == 1]
    )
    assert store['qualitative_true_positives_{}'.format(exp[:-11])] \
        == len(comparative_dataframe.index)
