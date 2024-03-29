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
from builtins import zip


try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from os.path import dirname, join

import pytest
from jsonschema import Draft4Validator, ValidationError
from numpy import isclose

from memote.experimental.config import ExperimentConfiguration


DATA_PATH = join(dirname(__file__), "data")


def test_configuration_schema():
    """Validate the schema itself against its specification."""
    with files("memote.experimental.schemata").joinpath("configuration.json").open(
        mode="r", encoding="utf-8"
    ) as file_handle:
        schema = json.load(file_handle)
    Draft4Validator.check_schema(schema)  # Will raise an exception if invalid.


@pytest.mark.parametrize(
    "filename",
    [
        pytest.param("empty.yml", marks=pytest.mark.raises(exception=ValidationError)),
        pytest.param(
            "invalid.yml", marks=pytest.mark.raises(exception=ValidationError)
        ),
        "valid.yml",
        "medium_only.yml",
    ],
)
def test_configuration(filename):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()


@pytest.mark.parametrize(
    "filename, model, media, growth",
    [
        (
            "medium_only.yml",
            "textbook",
            ["glucose", "m9_fructose", "pyruvate"],
            [0.874, 0.416, 0.291],
        )
    ],
    indirect=["model"],
)
def test_load_medium(filename, model, media, growth):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()
    config.load_medium(model)
    for medium_id, value in zip(media, growth):
        assert medium_id in config.media
        with model:
            config.media[medium_id].apply(model)
            assert isclose(model.slim_optimize(), value, atol=1e-03)


@pytest.mark.parametrize(
    "filename, model, experiment",
    [("essentiality_only.yml", "textbook", "core_deletion")],
    indirect=["model"],
)
def test_load_essentiality(filename, model, experiment):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()
    config.load_medium(model)
    config.load_essentiality(model)
    exp = config.essentiality[experiment]
    expected = exp.data
    expected.sort_values("gene", inplace=True)
    test = exp.evaluate(model)
    test.sort_values("gene", inplace=True)
    assert (test["essential"].values == expected["essential"].values).all()


@pytest.mark.parametrize(
    "filename, model, experiment",
    [("growth.yml", "textbook", "core")],
    indirect=["model"],
)
def test_load_growth(filename, model, experiment):
    config = ExperimentConfiguration(join(DATA_PATH, filename))
    config.validate()
    config.load_medium(model)
    config.load_growth(model)
    exp = config.growth[experiment]
    expected = exp.data
    expected.sort_values("exchange", inplace=True)
    test = exp.evaluate(model)
    test.sort_values("exchange", inplace=True)
    assert (test["growth"].values == expected["growth"].values).all()
