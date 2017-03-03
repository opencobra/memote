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
from datetime import datetime

import pytest


class ResultCollectionPlugin:
    """
    """

    def __init__(self, collect=True, filename=u"json.test"):
        """
        Collect and store values during testing.

        Parameters
        ----------
        collect : bool
            Whether to store values or perform dummy operations.
        filename : str or path
            Path of the JSON file where collected items are stored.
        """
        self._collect = bool(collect)
        if self._collect:
            self._store = dict()
        else:
            self._store = None
            self.__class__.__setitem__ = self.__class__._dummy_set
        self._time = None
        self._filename = filename

    def __setitem__(self, key, value):
        self._store[key] = value

    def _dummy_set(self, key, value):
        pass

    @pytest.fixture(autouse=True, scope="session")
    def store(self):
        return self

    def pytest_sessionstart(self):
        if not self._collect:
            return
        self._store["utc_timestamp"] = datetime.utcnow().isoformat(" ")

    def pytest_sessionfinish(self):
        if not self._collect:
            return
        with io.open(self._filename, "w", encoding=None) as file_h:
            json.dump(self._store, file_h, sort_keys=True)

    def pytest_terminal_summary(self, terminalreporter):
        if not self._collect:
            return
        terminalreporter.write_sep(
            u"-", u"generated json file: '{0}'".format(self._filename))
