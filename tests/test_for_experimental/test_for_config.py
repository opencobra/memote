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

"""Ensure the expected functioning of ``memote.suite.io.config``."""

from __future__ import absolute_import

import json
from jsonschema import Draft4Validator, ValidationError
from os.path import dirname, join
from builtins import zip

import pytest
from importlib_resources import open_text
from numpy import isclose

from memote.experimental.config import ExperimentConfiguration

DATA_PATH = join(dirname(__file__), "data")


def test_configuration_schema():
    """Validate the schema itself against its specification."""
    with open_text("memote.experimental.schemata", "configuration.json",
                   encoding="utf-8") as file_handle:
        schema = json.load(file_handle)
    Draft4Validator.check_schema(schema)  # Will raise an exception if invalid.


@pytest.mark.parametrize("filename", [
    pytest.mark.raises("empty.yml", exception=ValidationError),
    pytest.mark.raises("invalid.yml", exception=ValidationError),
    "valid.yml",
    "medium_only.yml"
])
def test_configuration(filename):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()


@pytest.mark.parametrize("filename, model, media, growth", [
    ("medium_only.yml", "textbook",
     [u"glucose", u"m9_fructose", u"pyruvate"],
     [0.874, 0.416, 0.291])
], indirect=["model"])
def test_load_medium(filename, model, media, growth):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()
    config.load_medium(model)
    for medium_id, value in zip(media, growth):
        assert medium_id in config.media
        with model:
            config.media[medium_id].apply(model)
            assert isclose(model.slim_optimize(), value, atol=1E-03)


@pytest.mark.parametrize("filename, model, experiment, genes, essentiality", [
    (u"essentiality_only.yml", "textbook",
     u"core_deletion",
     [u"b1779", u"b2416", u"b0356", u"b3213"],
     [True, True, False, False])
], indirect=["model"])
def test_load_essentiality(filename, model, experiment, genes, essentiality):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()
    config.load_essentiality(model)
    test = config.essentiality[experiment].evaluate(model)
    assert test.loc[genes, "essential"].tolist() == essentiality


@pytest.mark.parametrize("filename, model, growth", [
    ("growth.yml", "textbook",
     [0.874, 0.416, 0.291])
], indirect=["model"])
def test_load_growth(filename, model, growth):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()
    config.load_medium(model)
    config.load_growth(model)
    test = config.growth["core"]
    with model:
        for row in test.data.itertuples(index=False):
            config.media[row.medium].apply(model)
            value = model.slim_optimize()
            assert isclose(value, row.growth, atol=1E-03)
