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


class DummyDict(object):
    """
    Expose a fake `__setitem__` interface.
    """
    def __setitem__(self, key, value):
        pass


class ResultCollectionPlugin:
    """
    """

    def __init__(self, collect, filename):
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
            self._store["meta"] = self._meta = dict()
            self._store["test_data"] = self._data = dict()
        else:
            self._store = DummyDict()
            self._meta = DummyDict()
            self._data = DummyDict()
            self.__class__.__setitem__ = self.__class__._dummy_set
        self._filename = filename

    def __setitem__(self, key, value):
        self._data[key] = value

    @pytest.fixture(scope="module")
    def store(self, request):
        if self._collect:
            mod = request.module.__name__
            self._data[mod] = store = dict()
        else:
            store = self._data
        return store

    def pytest_sessionstart(self):
        if not self._collect:
            return
        self._meta["utc_timestamp"] = datetime.utcnow().isoformat(" ")

    def pytest_sessionfinish(self):
        if not self._collect:
            return
        with io.open(self._filename, "w", encoding=None) as file_h:
            json.dump(self._store, file_h, sort_keys=True, indent=4,
                      separators=(",", ": "))

    def pytest_terminal_summary(self, terminalreporter):
        if not self._collect:
            return
        terminalreporter.write_sep(
            u"*", u"update JSON file: '{0}'".format(self._filename))
