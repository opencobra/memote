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

"""
Collect results for reporting model quality.
"""

from __future__ import absolute_import

import io
try:
    import simplejson as json
except ImportError:
    import json
from builtins import dict

import pytest


class ResultCollectionPlugin:
    def __init__(self):
        self._store = dict()
        self._filename = u"test.json"

    @pytest.hookimpl(hookwrapper=True)
    def pytest_pyfunc_call(self, pyfuncitem):
        outcome = yield
        if outcome.excinfo is None:
            self._store[pyfuncitem.name] = outcome.get_result()
        else:
            self._store[pyfuncitem.name] = None

    def pytest_sessionfinish(self):
        with io.open(self._filename, "w", encoding=None) as file_h:
            json.dump(self._store, file_h)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep(
            u"-", u"generated json file: '{0}'".format(self._filename))
