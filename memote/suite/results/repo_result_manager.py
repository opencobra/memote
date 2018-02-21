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

    def __init__(self, location, **kwargs):
        """

        Parameters
        ----------
        location : str
            The directory for storing JSON files.

        """
        super(RepoResultManager, self).__init__(**kwargs)
        self.backend = location

    @staticmethod
    def record_git_info(repo, commit=None):
        """
        Record git meta information.

        Returns
        -------
        GitInfo
            Git commit meta information.
        """
        if commit is None:
            try:
                commit = repo.active_branch.commit
            except TypeError:
                LOGGER.error(
                    "Detached HEAD mode, please provide the commit hash.")
        else:
            commit = repo.commit(commit)
        return GitInfo(
            hexsha=commit.hexsha,
            author=commit.author.name,
            email=commit.author.email,
            authored_on=commit.authored_datetime
        )

    def get_filename(self, git_info):
        """"""
        return join(self.backend, "{}.json".format(git_info.hexsha))

    def store(self, result, repo, commit=None, pretty=True):
        """
        Store a result in a JSON file attaching git meta information.

        Parameters
        ----------
        result : dict
            The dictionary structure of a memote.MemoteResult.
        repo : git.Repo, optional
        commit : str, optional
            Unique hexsha of the desired commit.
        pretty : bool, optional
            Whether (default) or not to write JSON in a more legible format.

        """
        git_info = self.record_git_info(repo, commit)
        storage = dict()
        storage["results"] = result
        storage["hexsha"] = git_info.hexsha
        storage["author"] = git_info.author
        storage["email"] = git_info.email
        storage["authored_on"] = git_info.authored_on.isoformat(" ")
        filename = self.get_filename(git_info)
        super(RepoResultManager, self).store(
            storage, filename=filename, pretty=pretty)

    def load(self, repo, commit=None):
        """"""
        git_info = self.record_git_info(repo, commit)
        filename = self.get_filename(git_info)
        return super(RepoResultManager, self).load(filename)["results"]
