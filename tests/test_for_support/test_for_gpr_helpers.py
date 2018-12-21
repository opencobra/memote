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

"""Ensure the expected functioning of ``memote.support.gpr_helpers``."""

from __future__ import absolute_import

import pytest

from memote.support.gpr_helpers import find_top_level_complex


@pytest.mark.parametrize("gpr, expected", [
    ("gene1 and gene2", 2),
    ("gene1 or gene2", 0),
    ("gene1 and (gene2 or gene3)", 3)
])
def test_find_functional_units(gpr, expected):
    """Expect the size of the unique elements in a complex to be correct."""
    assert find_top_level_complex(gpr) == expected
