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
from memote.support.helpers import find_functional_units
import pytest

"""
Tests ensuring that the functions in `memote.support.helpers` work as expected.
"""


@pytest.mark.parametrize("gpr_str, expected", [
    ("gene1 and gene2", [["gene1", "gene2"]]),
    ("gene1 or gene2", [["gene1"], ["gene2"]]),
    ("gene1 and (gene2 or gene3)", [["gene1", "gene2"], ["gene1", "gene3"]])
])
def test_find_functional_units(gpr_str, expected):
    """Expect amount of enzyme complexes to be identified correctly."""
    assert list(find_functional_units(gpr_str)) == expected
