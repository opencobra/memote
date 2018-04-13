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

"""Test the functions in ``memote.support.essentiality``."""

from __future__ import absolute_import

from os.path import dirname, join

import cobra
import pandas as pd
import pytest

import memote.support.essentiality as essential
from memote.support.helpers import find_objective_function

MOCK_CONFIG = {
    'version': '0.1',
    'experiments': {
        'glucose': {'objectives': ['BIOMASS_TEST']},
        'mannose': {'objectives': ['BIOMASS_TEST']}
    }
}


@pytest.fixture(scope='module')
def genes():
    """Provides gene essentiality adapted from the Keio collection."""
    return ["b2935", "b0723", "b0451"]


@pytest.fixture(scope='module')
def expected_df():
    """Provides expected results generated using the E. coli core model."""
    return pd.DataFrame({
        "growth": [0.873922, 0.814298, 0.0],
        "gene": ["b2935", "b0723", "b0451"],
        "status": ["optimal", "optimal", "optimal"]
    })


@pytest.fixture(scope='function')
def raw_model():
    """Provides a raw model."""
    model = cobra.Model(id_or_model='raw_model', name='raw_model')
    rxn_1 = cobra.Reaction("BIOMASS_TEST")
    rxn_2 = cobra.Reaction("RXN2")
    rxn_3 = cobra.Reaction("RXN3")
    rxn_4 = cobra.Reaction("RXN4")
    model.add_reactions([rxn_1, rxn_2, rxn_3, rxn_4])
    model.objective = rxn_3
    return model


@pytest.fixture(scope='function')
def expected_model():
    """Provides a model with an objective function according to the config."""
    model = cobra.Model(id_or_model='expected_model', name='expected_model')
    rxn_1 = cobra.Reaction("BIOMASS_TEST")
    rxn_2 = cobra.Reaction("RXN2")
    rxn_3 = cobra.Reaction("RXN3")
    rxn_4 = cobra.Reaction("RXN4")
    model.add_reactions([rxn_1, rxn_2, rxn_3, rxn_4])
    model.objective = rxn_1
    return model


@pytest.mark.parametrize('config', [
    MOCK_CONFIG['experiments']['glucose'],
    MOCK_CONFIG['experiments']['mannose'],
    pytest.mark.raises({}, exception=KeyError)
])
def test_prepare_model_medium_objective(raw_model, expected_model, config):
    """Expect the objective function to be modified as defined."""
    essential.configure_model(raw_model, config)
    raw_id = find_objective_function(raw_model)[0].id
    expected_id = find_objective_function(expected_model)[0].id
    assert raw_id == expected_id


@pytest.mark.parametrize("model", ["textbook"], indirect=["model"])
def test_in_silico_essentiality(input_df, expected_df, model):
    """Expect the in silico result series to match the provided series."""
    in_silico = essential.in_silico_essentiality(model, input_df)
    assert in_silico[:2].equals(expected_df)


def test_prepare_essentiality_data(ijr904, combined_dataframe):
    """Expect the combined result dataframe to match the provided one."""
    tested_dataframe = essential.prepare_essentiality_data(
        join(dirname(__file__), 'data', 'essentiality', 'mock_essential.csv'),
        ijr904
    )
    assert tested_dataframe.equals(combined_dataframe)


def test_gene_essentiality_from_data_qualitative(combined_dataframe):
    """Expect that the amount of true positives can be determined correctly."""
    comparative_dataframe, exp = \
        essential.prepare_qualitative_comparison(combined_dataframe)
    assert len(comparative_dataframe[
        comparative_dataframe["true_positives"] == 1
    ]) == 3
