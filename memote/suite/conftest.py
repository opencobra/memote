# -*- coding: utf-8 -*-

# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability,
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

"""Configuration and fixtures for the test suite."""

from __future__ import absolute_import

import os
import warnings
from os.path import basename, splitext

import pytest
from cobra.io import read_sbml_model


MODELS = os.environ["MEMOTE_MODEL"].split(os.pathsep)
# MODELS = sorted(glob(join(dirname(__file__), "examples", "*.xml")))


@pytest.fixture(scope="session", params=MODELS,
                ids=[splitext(basename(mod))[0] for mod in MODELS])
def model(request):
    """Fixture that provides the model for the complete test session."""
    # TODO: deal with and record warnings on load
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return read_sbml_model(request.param)
