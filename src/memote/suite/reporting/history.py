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

import logging

from memote.suite.reporting.report import Report


LOGGER = logging.getLogger(__name__)


class HistoryReport(Report):
    """
    Render a rich report using the git repository history.

    Attributes
    ----------
    configuration : memote.MemoteConfiguration
        A memote configuration structure.

    """

    def __init__(self, history, configuration, **kwargs):
        """
        Initialize the git history report.

        Parameters
        ----------
        history : memote.HistoryManager
            An instance that manages access to test results.
        configuration : memote.MemoteConfiguration
            A memote configuration structure.


        """
        super(HistoryReport, self).__init__(
            result=None, configuration=configuration, **kwargs
        )
        self._report_type = "history"
        self._history = history
        self.config = configuration
        self.result = self.collect_history()
        self.result.update(self.config)

    def collect_history(self):
        """Build the structure of results in terms of a commit history."""

        def format_data(data):
            """Format result data according to the user-defined type."""
            # TODO Remove this failsafe once proper error handling is in place.
            if type == "percent" or data is None:
                # Return an empty list here to reduce the output file size.
                # The angular report will ignore the `data` and instead display
                # the `metric`.
                return []
            if type == "count":
                return len(data)
            return data

        base = dict()
        tests = base.setdefault("tests", dict())
        score = base.setdefault("score", dict())
        score_collection = score.setdefault("total_score", dict())
        for branch, commits in self._history.iter_branches():
            for commit in reversed(commits):
                result = self.result = self._history.get_result(commit)
                # Calculate the score for each result and store all the total
                # scores for each commit in the base dictionary.
                self.compute_score()
                total_score = self.result["score"]["total_score"]
                score_collection.setdefault("history", list())
                score_collection["format_type"] = "score"
                score_collection["history"].append(
                    {"branch": branch, "commit": commit, "metric": total_score}
                )
                # Now arrange the results for each test into the appropriate
                # format. Specifically such that the Accordion and the Vega
                # Plot components can easily read them.
                for test in result.cases:
                    tests.setdefault(test, dict())
                    if "title" not in tests[test]:
                        tests[test]["title"] = result.cases[test]["title"]
                    if "summary" not in tests[test]:
                        tests[test]["summary"] = result.cases[test]["summary"]
                    if "type" not in tests[test]:
                        tests[test]["format_type"] = result.cases[test]["format_type"]
                    type = tests[test]["format_type"]
                    metric = result.cases[test].get("metric")
                    data = result.cases[test].get("data")
                    res = result.cases[test].get("result")
                    if isinstance(metric, dict):
                        tests[test].setdefault("history", dict())
                        for param in metric:
                            tests[test]["history"].setdefault(param, list()).append(
                                {
                                    "branch": branch,
                                    "commit": commit,
                                    "metric": metric.get(param),
                                    "data": format_data(data.get(param)),
                                    "result": res.get(param),
                                }
                            )
                    else:
                        tests[test].setdefault("history", list()).append(
                            {
                                "branch": branch,
                                "commit": commit,
                                "metric": metric,
                                "data": format_data(data),
                                "result": res,
                            }
                        )
        return base
