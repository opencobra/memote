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

"""Collect results for reporting model quality."""

from __future__ import absolute_import

import io
import sys
try:
    import simplejson as json
except ImportError:
    import json
from builtins import dict
from datetime import datetime

import pytest
import git
import pip

from memote.suite.report import Report


class DummyDict(object):
    """Expose a fake `__setitem__` interface."""

    def __setitem__(self, key, value):
        """Dummy `__setitem__` method."""
        pass


class ResultCollectionPlugin:
    """
    Local pytest plugin that exposes a fixture for result collection.

    The plugin exposes the fixture `store` which can be used in test functions
    to store values in a dictionary. The dictionary is namespaced to the module
    so within a module the same keys should not be re-used (unless intended).
    """

    _valid_modes = frozenset(["collect", "basic", "html"])

    def __init__(self, mode="collect", filename=None, **kwargs):
        """
        Collect and store values during testing.

        Parameters
        ----------
        mode : {"collect", "basic", "html"}, optional
            The default is to "collect" test results and store them as JSON.
            Other modes include "basic" that simply runs the test suite and
            nothing more, or "html" that creates a pretty HTML report of the
            test results.
        filename : str, path, or None, optional
            Depending on `mode` the `filename` is the JSON output path in
            "collect" mode, `None` in "basic" mode, or the output path for the
            HTML report in "html" mode.
        """
        super(ResultCollectionPlugin, self).__init__(**kwargs)
        self._mode = mode.lower()
        assert self._mode in self._valid_modes
        if self._mode in ("collect", "html"):
            self._store = dict()
            self._store["meta"] = self._meta = dict()
            self._store["report"] = self._data = dict()
        else:
            self._store = DummyDict()
            self._meta = DummyDict()
            self._data = DummyDict()
            self.__class__.__setitem__ = self.__class__._dummy_set
        self._filename = filename

    @pytest.fixture(scope="module")
    def store(self, request):
        """Expose a `dict` to store values on."""
        if self._mode in ("collect", "html"):
            self._data[request.module.__name__] = store = dict()
        else:
            store = self._data
        return store

    def pytest_sessionstart(self):
        """Hook that runs at pytest session begin."""
        if self._mode == "basic":
            return
        self._meta["platform"] = sys.platform
        self._meta["python_version"] = sys.version
        if self._mode == "html":
            self._meta["timestamp"] = datetime.utcnow().isoformat(" ")
            return
        # allowed to fail
        if False:
            repo = git.Repo()
            if repo.is_dirty():
                raise RuntimeError(
                    "Please git commit or git stash all changes before running the"
                    " memote suite.")
            branch = repo.active_branch
            self._meta["branch"] = branch.name
            commit = branch.commit
            self._meta["commit_author"] = commit.author
            self._meta["timestamp"] = commit.committed_datetime.isoformat(" ")
            self._meta["commit_hash"] = commit.hexsha
            self._meta["python_environment"] = [
                str(dist.as_requirement()) for dist in
                pip.get_installed_distributions()]

    def pytest_sessionfinish(self):
        """Hook that runs at pytest session end."""
        if self._mode == "basic":
            return
        if self._mode == "html":
            report = Report(self._filename, self._store)
            with io.open(self._filename, "w", encoding="utf-8") as file_h:
                file_h.write(report.render_individual())
            return
        with io.open(self._filename, "w", encoding=None) as file_h:
            json.dump(self._store, file_h, sort_keys=True, indent=4,
                      separators=(",", ": "))

    def pytest_terminal_summary(self, terminalreporter):
        """Print the JSON file location if relevant."""
        if self._mode == "basic":
            return
        if self._mode == "html":
            terminalreporter.write_sep(
                u"*", u"generating report: '{0}'".format(self._filename))
            return
        terminalreporter.write_sep(
            u"*", u"update JSON file: '{0}'".format(self._filename))
