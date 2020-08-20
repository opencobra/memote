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

"""Provide an abstract report base class that sets the interface."""

from __future__ import absolute_import

import logging
from string import Template

from importlib_resources import read_text
from pandas import DataFrame
from six import iteritems, itervalues

import memote.suite.templates as templates
from memote.utils import jsonify


LOGGER = logging.getLogger(__name__)


class Report(object):
    """
    Determine the abstract report interface.

    Attributes
    ----------
    result : memote.MemoteResult
        The dictionary structure of results.
    configuration : memote.MemoteConfiguration
        A memote configuration structure.

    """

    def __init__(self, result, configuration, **kwargs):
        """
        Fuse a collective result with a report configuration.

        Parameters
        ----------
        result : memote.MemoteResult
            The dictionary structure of results.
        configuration : memote.MemoteConfiguration
            A memote configuration structure.

        """
        super(Report, self).__init__(**kwargs)
        self.result = result
        self.config = configuration
        self._report_type = None
        self._template = Template(read_text(templates, "index.html", encoding="utf-8"))

    def render_json(self, pretty=False):
        """
        Render the report results as JSON.

        Parameters
        ----------
        pretty : bool, optional
            Whether to format the resulting JSON in a more legible way (
            default False).

        """
        return jsonify(self.result, pretty=pretty)

    def render_html(self):
        """Render an HTML report."""
        return self._template.safe_substitute(
            report_type=self._report_type, results=self.render_json()
        )

    def get_configured_tests(self):
        """Get tests explicitly configured."""
        tests_on_cards = set()
        # Add scored tests to the set.
        for card in itervalues(self.config["cards"]["scored"]["sections"]):
            tests_on_cards.update(card.get("cases", []))
        # Add all other tests.
        for card, content in iteritems(self.config["cards"]):
            if card == "scored":
                continue
            tests_on_cards.update(content.get("cases", []))
        return tests_on_cards

    def determine_miscellaneous_tests(self):
        """
        Identify tests not explicitly configured in test organization.

        List them as an additional card called `Misc`, which is where they will
        now appear in the report.

        """
        tests_on_cards = self.get_configured_tests()
        self.config["cards"].setdefault("misc", dict())
        self.config["cards"]["misc"]["title"] = "Misc. Tests"
        self.config["cards"]["misc"]["cases"] = list(
            set(self.result.cases) - set(tests_on_cards)
        )

    def compute_score(self):
        """Calculate the overall test score using the configuration."""
        # LOGGER.info("Begin scoring")
        cases = self.get_configured_tests() | set(self.result.cases)
        scores = DataFrame({"score": 0.0, "max": 1.0}, index=sorted(cases))
        self.result.setdefault("score", dict())
        self.result["score"]["sections"] = list()
        # Calculate the scores for each test individually.
        for test, result in iteritems(self.result.cases):
            # LOGGER.info("Calculate score for test: '%s'.", test)
            # Test metric may be a dictionary for a parametrized test.
            metric = result["metric"]
            if hasattr(metric, "items"):
                result["score"] = test_score = dict()
                total = 0.0
                for key, value in iteritems(metric):
                    value = 1.0 - value
                    total += value
                    test_score[key] = value
                # For some reason there are parametrized tests without cases.
                if len(metric) == 0:
                    metric = 0.0
                else:
                    metric = total / len(metric)
            else:
                metric = 1.0 - metric
            scores.at[test, "score"] = metric
            scores.loc[test, :] *= self.config["weights"].get(test, 1.0)
        score = 0.0
        maximum = 0.0
        # Calculate the scores for each section considering the individual test
        # case scores.
        for section_id, card in iteritems(self.config["cards"]["scored"]["sections"]):
            # LOGGER.info("Calculate score for section: '%s'.", section_id)
            cases = card.get("cases", None)
            if cases is None:
                continue
            card_score = scores.loc[cases, "score"].sum()
            card_total = scores.loc[cases, "max"].sum()
            # Format results nicely to work immediately with Vega Bar Chart.
            section_score = {"section": section_id, "score": card_score / card_total}
            self.result["score"]["sections"].append(section_score)
            # Calculate the final score for the entire model.
            weight = card.get("weight", 1.0)
            score += card_score * weight
            maximum += card_total * weight
        self.result["score"]["total_score"] = score / maximum
