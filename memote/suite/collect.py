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
import platform
import logging

from builtins import dict
from datetime import datetime

import pytest
import pip

from memote.support.helpers import find_biomass_reaction

LOGGER = logging.getLogger(__name__)


class ResultCollectionPlugin(object):
    """
    Provide functionality for complex test result collection.

    The plugin exposes the fixture ``store`` which can be used in test functions
    to store values in a dictionary. The dictionary is namespaced to the module
    so within a module the same keys should not be re-used (unless intended).

    """

    def __init__(self, model, repository=None, branch=None, commit=None,
                 **kwargs):
        """
        Collect and store values during testing.

        Parameters
        ----------
        model : cobra.Model
            The metabolic model under investigation.
        repository : git.Repo, optional
            An instance of the git repository (if any).
        branch : str, optional
            The name of the git branch to use.
        commit : str, optional
            The specific commit hash that is being tested.

        """
        super(ResultCollectionPlugin, self).__init__(**kwargs)
        self._model = model
        self._store = dict()
        self._store["meta"] = self._meta = dict()
        self._store["report"] = self._data = dict()
        self.repo = repository
        self.branch = branch
        self.commit = commit
        self._collect_meta_info()

    def _collect_meta_info(self):
        """Record environment information."""
        os.environ["BIOMASS_REACTIONS"] = "|".join([
            rxn.id for rxn in find_biomass_reaction(self._model)])
        self._meta["platform"] = platform.system()
        self._meta["release"] = platform.release()
        self._meta["python"] = platform.python_version()
        self._meta["packages"] = dict(
            (dist.project_name, dist.version) for dist in
            pip.get_installed_distributions())
        self._meta["timestamp"] = datetime.utcnow().isoformat(" ")
        if self.repo is not None:
            self._collect_git_info()

    def _collect_git_info(self):
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

    @property
    def results(self):
        """Return the test results as a nested dictionary."""
        return self._store

    @pytest.fixture(scope="session")
    def read_only_model(self):
        """Provide the model for the complete test session."""
        return self._model

    @pytest.fixture(scope="function")
    def model(self, read_only_model):
        """Provide a pristine model for a test unit."""
        return self._model.copy()

    @pytest.fixture(scope="module")
    def store(self, request):
        """Expose a `dict` to store values on."""
        LOGGER.debug("requested in '%s'", request.module.__name__)
        self._data[request.module.__name__] = dict()
        return self._data[request.module.__name__]
