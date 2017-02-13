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
from cobra import Model


@pytest.fixture(scope="function")
def model(request):
    if request.param == "empty":
        return Model(id_or_model=request.param, name=request.param)
    else:
        builder = getattr(request.module, "model_builder")
        return builder(request.param)


@pytest.fixture(scope="session",
                params=["e", "pp", "c"])
def compartment_suffix(request):
    return request.param
