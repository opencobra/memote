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

"""Ensure the expected functioning of ``memote.suite.cli.callbacks``."""

from __future__ import absolute_import

import memote.suite.cli.callbacks as callbacks


def test_validate_model(model_file):
    """Expect a valid returned model."""
    model = callbacks.validate_model(None, "model", model_file)
    assert model.id == "MODELID_3473243"
    assert len(model.metabolites) == 72
    assert len(model.reactions) == 95
