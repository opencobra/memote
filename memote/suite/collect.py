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

import os
import io
import platform
import logging

try:
    import simplejson as json
except ImportError:
    import json
import warnings
from builtins import dict
from datetime import datetime

import pytest
import pip
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    # ignore Gurobi warning
    from cobra.io import read_sbml_model

from memote.suite.reporting.reports import BasicReport
from memote.support.helpers import find_biomass_reaction

LOGGER = logging.getLogger(__name__)


class ResultCollectionPlugin(object):
    """
    Local pytest plugin that exposes a fixture for result collection.

    The plugin exposes the fixture `store` which can be used in test functions
    to store values in a dictionary. The dictionary is namespaced to the module
    so within a module the same keys should not be re-used (unless intended).

    """

    _valid_modes = frozenset(["collect", "git-collect", "basic", "html"])

    def __init__(self, model, mode="collect", filename=None, directory=None,
                 repo=None, branch=None, commit=None, **kwargs):
        """
        Collect and store values during testing.

        Parameters
        ----------
        model : str or path
            Path to model that is to be tested in the suite.
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
        self._model = model
        self.mode = mode.lower()
        assert self.mode in self._valid_modes
        self._store = dict()
        self._store["meta"] = self._meta = dict()
        self._store["report"] = self._data = dict()
        self.filename = filename
        self.directory = directory
        self.repo = repo
        self.branch = branch
        self.commit = commit
        # TODO: record SBML warnings and add them to the report
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self._sbml_model = read_sbml_model(self._model)

    def _git_meta_info(self):
        """Record repository meta information."""
        if self.branch is None:
            try:
                self.branch = self.repo.active_branch
            except TypeError:
                LOGGER.error(
                    "Detached HEAD mode, please provide the branch name and"
                    " commit hash.")
            except AttributeError:
                LOGGER.error("No git repository found.")
        if self.branch is not None:
            self._meta["branch"] = self.branch.name
        if self.commit is None:
            try:
                self.commit = self.branch.commit
            except AttributeError:
                LOGGER.error("No git repository found.")
        if self.commit is not None:
            self._meta["commit_author"] = self.commit.author.name
            self._meta["timestamp"] = self.commit.committed_datetime.isoformat(
                " ")
            self._meta["commit_hash"] = self.commit.hexsha

    @pytest.fixture(scope="session")
    def read_only_model(self):
        """Provide the model for the complete test session."""
        return self._sbml_model

    @pytest.fixture(scope="function")
    def model(self, read_only_model):
        """Provide a pristine model for a test unit."""
        return read_only_model.copy()

    @pytest.fixture(scope="module")
    def store(self, request):
        """Expose a `dict` to store values on."""
        LOGGER.debug("requested in '%s'", request.module.__name__)
        if self.mode in ("collect", "git-collect", "html"):
            self._data[request.module.__name__] = store = dict()
        else:
            store = self._data
        return store

    def pytest_sessionstart(self):
        """Record environment information of the pytest session."""
        os.environ["BIOMASS_REACTIONS"] = "|".join([
            rxn.id for rxn in find_biomass_reaction(self._sbml_model)])
        if self.mode == "basic":
            return
        self._meta["platform"] = platform.system()
        self._meta["release"] = platform.release()
        self._meta["python"] = platform.python_version()
        self._meta["packages"] = dict(
            (dist.project_name, dist.version) for dist in
            pip.get_installed_distributions())
        if self.mode == "html":
            self._meta["timestamp"] = datetime.utcnow().isoformat(" ")
            return
        if self.mode == "git-collect":
            self._git_meta_info()

    def pytest_sessionfinish(self):
        """Create output at the end of the session."""
        if self.mode == "basic":
            return
        if self.mode == "html":
            report = BasicReport(self._store)
            with io.open(self.filename, "w") as file_h:
                file_h.write(report.render_html())
            return
        with open(self.filename, "w") as file_h:
            json.dump(self._store, file_h, sort_keys=True, indent=4,
                      separators=(",", ": "))

    def pytest_terminal_summary(self, terminalreporter):
        """Print the JSON file location if relevant."""
        if self.mode == "basic":
            return
        if self.mode == "html":
            terminalreporter.write_line(
                u"writing report '{0}'".format(self.filename))
            return
        terminalreporter.write_line(
            u"writing JSON output '{0}'".format(self.filename))
