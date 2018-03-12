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

"""Provide a memote result manager that integrates with a git repository."""

from __future__ import absolute_import

import logging
from collections import namedtuple
from os.path import join

from memote.suite.results.result_manager import ResultManager

__all__ = ("RepoResultManager",)

LOGGER = logging.getLogger(__name__)


GitInfo = namedtuple("GitInfo", ["hexsha", "author", "email", "authored_on"])


class RepoResultManager(ResultManager):
    """
    Manage storage of results to JSON files.

    Results are stored to and loaded from a specific location (directory) and
    enriched with git commit meta information.

    """

    def __init__(self, repository, location, **kwargs):
        """
        Initialize the repository aware JSON file storage manager.

        Parameters
        ----------
        repository : git.Repo
            The current repository.
        location : str or pathlib.Path
            The directory for storing JSON files.

        """
        super(RepoResultManager, self).__init__(**kwargs)
        self._repo = repository
        self._backend = location

    def record_git_info(self, commit=None):
        """
        Record git meta information.

        Parameters
        ----------
        commit : str, optional
            Unique hexsha of the desired commit.

        Returns
        -------
        GitInfo
            Git commit meta information.

        """
        if commit is None:
            commit = self._repo.head.commit
        else:
            commit = self._repo.commit(commit)
        return GitInfo(
            hexsha=commit.hexsha,
            author=commit.author.name,
            email=commit.author.email,
            authored_on=commit.authored_datetime
        )

    def get_filename(self, git_info):
        """
        Create a filename from the storage directory and the commit hash.

        Parameters
        ----------
        git_info : GitInfo
            A named tuple with git meta information.

        Returns
        -------
        str
            The path to the file where the result of the current commit is
            stored.

        """
        return join(self._backend, "{}.json".format(git_info.hexsha))

    @staticmethod
    def add_git(meta, git_info):
        """Enrich the result meta information with commit data."""
        meta["hexsha"] = git_info.hexsha
        meta["author"] = git_info.author
        meta["email"] = git_info.email
        meta["authored_on"] = git_info.authored_on.isoformat(" ")

    def store(self, result, commit=None, **kwargs):
        """
        Store a result in a JSON file attaching git meta information.

        Parameters
        ----------
        result : memote.MemoteResult
            The dictionary structure of results.
        commit : str, optional
            Unique hexsha of the desired commit.
        kwargs :
            Passed to parent function.

        """
        git_info = self.record_git_info(commit)
        self.add_git(result.meta, git_info)
        filename = self.get_filename(git_info)
        super(RepoResultManager, self).store(
            result, filename=filename, **kwargs)

    def load(self, commit=None):
        """Load a result from the storage directory."""
        git_info = self.record_git_info(commit)
        filename = self.get_filename(git_info)
        result = super(RepoResultManager, self).load(filename)
        self.add_git(result.meta, git_info)
        return result
