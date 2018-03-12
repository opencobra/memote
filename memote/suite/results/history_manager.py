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

"""Provide a history manager that integrates with a git repository."""

from __future__ import absolute_import

import logging
import json

from six import iteritems, iterkeys
from sqlalchemy.orm.exc import NoResultFound

from memote.suite.results import MemoteResult

__all__ = ("HistoryManager",)

LOGGER = logging.getLogger(__name__)


class HistoryManager(object):
    """
    Manage access to results in the commit history of a git repository.

    Attributes
    ----------
    manager : memote.RepoResultManager
        The manager for accessing individual results.
    current : str
        The name of the currently active branch.

    """

    def __init__(self, repository, manager, **kwargs):
        """
        Initialize a manager to access results in the git history.

        Parameters
        ----------
        location : str
            The directory for storing JSON files.

        """
        super(HistoryManager, self).__init__(**kwargs)
        self._repo = repository
        self.manager = manager
        self._latest = self._repo.active_branch
        self._history = None
        self._results = None

    def reset(self):
        """Reset the git repository to head of the previously active branch."""
        self._repo.git.checkout(self._latest)

    def build_branch_structure(self):
        """Inspect and record the repo's branches and their history."""
        self._history = dict()
        self._history["commits"] = commits = dict()
        self._history["branches"] = branches = dict()
        skip = frozenset(["gh-pages"])
        for branch in self._repo.refs:
            LOGGER.debug(branch.name)
            if branch.name in skip:
                continue
            branches[branch.name] = branch_history = list()
            latest = branch.commit
            history = [latest] + list(latest.iter_parents())
            for commit in history:
                branch_history.append(commit.hexsha)
                if commit.hexsha not in commits:
                    commits[commit.hexsha] = sub = dict()
                    sub["timestamp"] = commit.authored_datetime.isoformat(" ")
                    sub["author"] = commit.author.name
                    sub["email"] = commit.author.email
        LOGGER.debug("%s", json.dumps(self._history, indent=2))
        self.reset()

    def iter_branches(self):
        """Iterate over branch names and their commit histories."""
        return iteritems(self._history["branches"])

    def iter_commits(self):
        """Iterate over all commit hashes in the repository."""
        return iterkeys(self._history["commits"])

    def load_history(self):
        """
        Load the entire results history into memory.

        Could be a bad idea in a far future.

        """
        assert self._history is not None, \
            "Please call the method `build_branch_structure` first."
        self._results = dict()
        all_commits = list(self._history["commits"])
        for commit in all_commits:
            try:
                self._results[commit] = self.manager.load(commit)
            except (IOError, NoResultFound) as err:
                LOGGER.error("Could not load result '%s'.", commit)
                LOGGER.debug("%s", str(err))

    def get_result(self, commit, default=MemoteResult()):
        """Return an individual result from the history if it exists."""
        assert self._results is not None, \
            "Please call the method `load_history` first."
        return self._results.get(commit, default)
