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
Tests for functions in `memote.support.data.genome` to work as expected.
"""

from __future__ import absolute_import

from os.path import dirname, join, basename
from tempfile import gettempdir

import cobra
import pandas as pd
import pytest

import memote.support.experimental.essentiality as essential
from memote.support.helpers import find_objective_function

mock_config_dict = {'essentiality': {
    'glucose': {'objective': 'BIOMASS_TEST'},
    'mannose': {'objective': 'BIOMASS_TEST'}}
}


@pytest.fixture(scope='function')
def input_series():
    """Provides gene essentiality series adapted from the Keio Collection"""
    return pd.Series(
        data=[0.0, 0.0, 0.183, 0.0],
        index=['b0025', 'b0417', 'b0418', 'b0893']
    )


@pytest.fixture(scope='function')
def expected_series():
    """Provides expected results series generated using default iJR904"""
    return pd.Series(
        data=[0.0, 0.922, 0.922, 0],
        index=['b0025', 'b0417', 'b0418', 'b0893']
    )


@pytest.fixture(scope='function')
def combined_dataframe(input_series, expected_series):
    """Provides expected essentiality dataframe using default iJR904"""
    essentiality_dataframe = {
        'data/e_mock_essential_experiment': input_series,
        'data/e_mock_essential_model': expected_series
    }
    return pd.DataFrame(essentiality_dataframe)


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


@pytest.fixture(scope='function')
def ijr904():
    """Provides iJR904 with an objective function according to the config."""
    # Growth on glycerol minimal medium was simulated by maximizing flux
    # through a defined biomass objective function and allowing the uptake of
    # glycerol, NH4, SO4, O2, and Pi and the free exchange of H+, H2O, and CO2.
    filename = './tests/data/iJR904.xml.gz'
    model = cobra.io.read_sbml_model(filename)
    return model


@pytest.mark.parametrize("directory, expected", [
    (join(dirname(__file__), 'data'), [
        'glucose.csv',
        'mannose.csv',
        'mock_essential.csv'
    ]),
    (gettempdir(), [])
])
def test_essentiality_file_paths(directory, expected):
    """Expect that .csv files can be identified."""
    files = essential.essentiality_file_paths(directory)
    assert [basename(f) for f in files] == expected


@pytest.mark.parametrize("filepath, expected", [
    (join(dirname(__file__), 'data', 'config.yml'), mock_config_dict),
    ('/data/', None)
])
def test_load_experiment_data_config(filepath, expected):
    """Expect that config.yml files can be identified."""
    config = essential.load_experiment_data_config(filepath)
    assert config == expected


def test_prepare_model_medium_objective(raw_model, expected_model):
    """Expect the objective function to be modified as defined in config."""
    tested_model = essential.prepare_model_medium(
        raw_model, 'essentiality', 'glucose', mock_config_dict
    )
    assert find_objective_function(tested_model)[0].id \
        == find_objective_function(expected_model)[0].id


def test_prepare_model_medium_none_config(raw_model):
    """Expect the objective function to be modified as defined in config."""
    tested_model = essential.prepare_model_medium(
        raw_model, 'essentiality', 'glucose', None
    )
    assert tested_model is None


def test_in_silico_essentiality(input_series, expected_series, ijr904):
    """Expect the in silico result series to match the provided series."""
    tested_in_silico_series = essential.in_silico_essentiality(
        input_series, ijr904
    )
    assert tested_in_silico_series.equals(expected_series)


def test_prepare_essentiality_data(ijr904, combined_dataframe):
    """Expect the combined result dataframe to match the provided one."""
    tested_dataframe = essential.prepare_essentiality_data(
        join(dirname(__file__), 'data', 'mock_essential.csv'),
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
