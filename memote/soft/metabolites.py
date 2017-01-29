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

"""
The module provides soft expectations on model metabolites that will mostly
generate log output and warnings but will likely not fail a test suite.
"""

from __future__ import absolute_import

__all__ = ("check_formula_presence",)

import logging

LOGGER = logging.getLogger(__name__)


def check_formula_presence(model):
    return [met for met in model.metabolites if not met.formula]
