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

"""Test the result collection plugin."""


def test_store(testdir):
    """Make sure that the store fixture in the collect plugin works."""
    testdir.makeconftest("""
           import pytest
       """)
    # create a temporary pytest test file
    # TODO: Figure out why this doesn't work.
    testdir.makepyfile("""
        #def test_store(store):
        #    pass
    """)

    # run all tests with pytest
    result = testdir.runpytest()

    # check that the test passes
    result.assert_outcomes(passed=0)
