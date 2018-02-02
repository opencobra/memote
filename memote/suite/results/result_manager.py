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

"""Provide the memote result managers for various storage backends."""

from __future__ import absolute_import

import json
import logging
from collections import namedtuple
from os.path import join

from future.utils import raise_with_traceback

from memote.utils import log_json_incompatible_types

LOGGER = logging.getLogger(__name__)


GitInfo = namedtuple("GitInfo", ["hexsha", "author", "email", "authored_on"])


class ResultManager(object):

    def __init__(self, connector, **kwargs):
        """

        Parameters
        ----------
        connector : str
            The directory for storing JSON files.

        """
        super(ResultManager, self).__init__(**kwargs)
        self.backend = connector

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
            authored_on=commit.authored_datetime.isoformat(" ")
        )

    def store(self, result, repo=None, commit=None, filename=None):
        """
        Safe a result to the chosen backend attaching git information.

        Parameters
        ----------
        result : memote.MemoteResult
        repo : git.Repo, optional
        commit : str, optional
            Unique hexsha of the desired commit.
        filename : str, optional
            Store results directly to the given filename ignoring an existing
            git repository.

        """
        if filename is not None:
            storage = result.store
        else:
            git_info = self.record_git_info(repo, commit)
            storage = dict()
            storage["results"] = result.store
            storage["hexsha"] = git_info.hexsha
            storage["author"] = git_info.author
            storage["email"] = git_info.email
            storage["authored_on"] = git_info.authored_on
            filename = join(self.backend, "{}.json".format(git_info.hexsha))
        with open(filename, "w") as file_handle:
            try:
                return json.dump(storage, file_handle, sort_keys=True,
                                 indent=2, separators=(",", ": "))
            except TypeError as error:
                log_json_incompatible_types(storage)
                raise_with_traceback(error)

    def load(self, repo, commit):
        pass
