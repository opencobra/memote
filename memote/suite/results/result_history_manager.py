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

"""Provide the memote result history manager."""

from __future__ import absolute_import

from six import itervalues

import logging

LOGGER = logging.getLogger(__name__)


class ResultHistoryManager(object):

    def __init__(self, history, manager, **kwargs):
        """

        Parameters
        ----------
        history : dict
            A mapping from git branch names to their commit history.
        manager : memote.ResultManager
            The chosen result storage backend.

        """
        super(ResultHistoryManager, self).__init__(**kwargs)
        self.history = history
        self.manager = manager
        self.results = dict()

    def load_history(self):
        """
        Load the entire results history into memory.

        Could be a bad idea in a far future.

        """
        all_commits = set()
        for commits in itervalues(self.history):
            all_commits.update(commits)
        for commit in all_commits:
            self.results[commit] = self.manager.load(commit)
