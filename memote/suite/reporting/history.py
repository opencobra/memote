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

"""Render results into pretty HTML."""

from __future__ import absolute_import

import json
import logging
from os.path import join
from builtins import str, open
from string import Template

from memote.utils import log_json_incompatible_types
from memote.suite.reporting import TEMPLATES_PATH
from memote.suite.results import HistoryManager

LOGGER = logging.getLogger(__name__)


class HistoryReport(object):
    """Render a rich report using the git repository history."""

    _valid_indexes = frozenset(["time", "hash"])

    def __init__(self, repository, manager, index="time", **kwargs):
        """
        Initialize the git history.

        Parameters
        ----------
        repository : git.Repo
            An instance of the working directory git repository.
        manager : memote.RepoResultManager
            The manager grants access to previous results.
        index : {'time', 'hash'}, optional
            Whether to use time (the default) or commit hashes as the default
            axis in plots.

        """
        super(HistoryReport, self).__init__(**kwargs)
        with open(
            join(TEMPLATES_PATH, "index.html"), encoding="utf-8"
        ) as file_path:
            self._template = Template(file_path.read())
        self.index_dim = index.lower()
        if self.index_dim not in self._valid_indexes:
            raise ValueError(
                "Given index '{0}' must be one of {1}."
                "".format(self.index_dim, str(self._valid_indexes)))
        self.repo = repository
        self.manager = manager
        self.history = HistoryManager(self.repo, self.manager)
        # self.index = {
        #     "time": "timestamp",
        #     "hash": "commit_hash"
        # }.get(index, ValueError("Unknown index type '{}'.".format(index)))
        # if isinstance(self.index, ValueError):
        #     raise self.index

    def collect_history(self):
        # Iter over past extending lists in results merged with configs.
        base = dict()
        for branch, commits in self.history.iter_branches():
            for commit in commits:
                result = self.history.get_result(commit, dict())
                for test in result["tests"]:
                    base.setdefault(test, dict()).setdefault("history", dict())
                    if "title" not in base[test]:
                        base[test]["title"] = result["tests"][test]["title"]
                    if "summary" not in base[test]:
                        base[test]["summary"] = result["tests"][test]["summary"]
                    if isinstance(result["tests"][test]["metric"], dict):
                        for param in result["tests"][test]["metric"]:
                            base[test]["history"].setdefault(param, dict()). \
                                setdefault(branch, list()).append({
                                    "commit": commit,
                                    "metric": result["tests"][test]["metric"][param]
                                })
                    else:
                        base[test]["history"].setdefault(branch, list()). \
                            append({
                                "commit": commit,
                                "metric": result["tests"][test]["metric"]
                            })
        return base

    def render_html(self):
        """
        Render a rich report for the repository.

        This is currently a stub while we convert from ``jinja2`` templates
        to a full Angular based report.
        """
        self.history.build_branch_structure()
        self.history.load_history()
        structure = self.collect_history()
        try:
            return self._template.safe_substitute(
                results=json.dumps(structure, sort_keys=False,
                                   indent=None, separators=(",", ":")))
        except TypeError:
            log_json_incompatible_types(structure)
