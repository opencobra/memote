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

from __future__ import absolute_import

"""
Configuration and fixtures for the py.test suite.
"""

import pytest

from os.path import (dirname, basename, join, splitext)
from glob import glob

from cameo import load_model

MODELS = sorted(glob(join(dirname(__file__), "data", "*.xml")))

#@pytest.fixture(scope="session")
#def model_paths():
#    return sorted(glob(join(dirname(__file__), "data", "*.xml")))

@pytest.fixture(scope="session", params=MODELS,
        ids=[splitext(basename(mod))[0] for mod in MODELS])
def model(request):
    return load_model(request.param)
