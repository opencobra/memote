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
from string import Template

from importlib_resources import read_text

import memote.suite.templates as templates
from memote.utils import log_json_incompatible_types

LOGGER = logging.getLogger(__name__)


class HistoryReport(object):
    """
    Render a rich report using the git repository history.

    Attributes
    ----------
    configuration : memote.MemoteConfiguration
        A memote configuration structure.
    """

    _valid_indexes = frozenset(["time", "hash"])

    def __init__(self, history, configuration, index="hash", **kwargs):
        """
        Initialize the git history report.

        Parameters
        ----------
        history : memote.HistoryManager
            An instance that manages access to test results.
        index : {"hash", "time"}, optional
            The default horizontal axis type for all plots.
        """
        super(HistoryReport, self).__init__(**kwargs)
        self._template = Template(
            read_text(templates, "index.html", encoding="utf-8"))
        self._history = history
        self.config = configuration

    def collect_history(self):
        """Build the structure of results in terms of a commit history."""
        def get_specific_result_attribute_from_key(key):
            """Collect a specific result attribute from each test case"""
            value = result.cases[test].get(key)
            if isinstance(value, dict):
                for param in value:
                    tests[test]["history"].setdefault(param, dict()). \
                        setdefault(branch, list()).append({
                            "commit": commit,
                            key: value.get(param)})
            else:
                tests[test]["history"].setdefault(branch, list()). \
                    append({
                        "commit": commit,
                        key: value})

        base = dict()
        tests = base.setdefault("tests", dict())
        for branch, commits in self._history.iter_branches():
            for commit in commits:
                result = self._history.get_result(commit, )
                for test in result.cases:
                    tests.setdefault(test, dict()).setdefault(
                        "history", dict())
                    if "title" not in tests[test]:
                        tests[test]["title"] = result.cases[test]["title"]
                    if "summary" not in tests[test]:
                        tests[test]["summary"] = result.cases[test]["summary"]
                    if "type" not in tests[test]:
                        tests[test]["type"] = result.cases[test]["type"]
                    get_specific_result_attribute_from_key("metric")
                    get_specific_result_attribute_from_key("data")
                    get_specific_result_attribute_from_key("result")
        return base

    def render_html(self):
        """Render a rich report for the repository."""
        self._history.build_branch_structure()
        self._history.load_history()
        structure = self.collect_history()
        structure.update(self.config)
        try:
            return self._template.safe_substitute(
                results=json.dumps(structure, sort_keys=False,
                                   indent=None, separators=(",", ":")))
        except TypeError:
            log_json_incompatible_types(structure)
