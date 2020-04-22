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

"""Ensure the expected functioning of ``memote.suite.io.config``."""

from __future__ import absolute_import

from os.path import dirname, join

import pytest
from six import iteritems

from memote.experimental.experimental_base import ExperimentalBase
from memote.experimental.medium import Medium
from memote.experimental.experiment import Experiment
from memote.experimental.essentiality import EssentialityExperiment
from memote.experimental.growth import GrowthExperiment

DATA_PATH = join(dirname(__file__), "data")


@pytest.fixture(scope="module", params=[
    ExperimentalBase,
    Medium,
    Experiment,
    EssentialityExperiment,
    GrowthExperiment
])
def klass(request):
    return request.param


@pytest.mark.parametrize("obj", [
    {},
    {"label": "bird"}
])
def test_init(klass, obj):
    kwargs = {
        "identifier": "that",
        "obj": obj,
        "filename": join(DATA_PATH, "."),
    }
    if issubclass(klass, Experiment):
        # minimal_growth_rate is required and only used by classes derived
        # from Experiment (GrowthExperiment and EssentialityExperiment)
        kwargs["minimal_growth_rate"] = 0.002
    exp = klass(**kwargs)
    for key, value in iteritems(obj):
        assert getattr(exp, key) == value


def test_load():
    pass


def test_validate():
    pass


def test_evaluate_report():
    pass
