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

from pandas import DataFrame
from six import iteritems, itervalues

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

    def render_html(self):
        """Render an HTML report."""
        raise NotImplementedError("Abstract method.")

    def determine_miscellaneous_tests(self):
        """
        Identify tests not explicitly configured in test organization.

        List them as an additional card called `Misc`, which is where they will
        now appear in the report.

        """
        tests_on_cards = set()
        # Add scored tests to the set.
        for card in itervalues(self.config["cards"]["scored"]["sections"]):
            tests_on_cards.update(card.get("cases", []))
        # Add all other tests.
        for card, content in iteritems(self.config["cards"]):
            if card == "scored":
                continue
            tests_on_cards.update(content.get("cases", []))

        self.config["cards"].setdefault("misc", dict())
        self.config["cards"]["misc"]["title"] = "Misc. Tests"
        self.config["cards"]["misc"]["cases"] = list(
            set(self.result.cases) - set(tests_on_cards))

    def compute_score(self):
        """Calculate the overall test score using the configuration."""
        scores = DataFrame({"score": 1.0, "max": 1.0},
                           index=list(self.result.cases))
        for test, result in iteritems(self.result.cases):
            # Test metric may be a dictionary for a parametrized test.
            metric = result["metric"]
            if hasattr(metric, "items"):
                result["score"] = test_score = dict()
                total = 0.0
                for key, value in iteritems(metric):
                    total += value
                    test_score[key] = 1.0 - value
                # For some reason there are parametrized tests without cases.
                if len(metric) == 0:
                    metric = 1.0
                else:
                    metric = total / len(metric)
            else:
                result["score"] = 1.0 - metric
            scores.at[test, "score"] -= metric
            scores.loc[test, :] *= self.config["weights"].get(test, 1.0)
        score = 0.0
        maximum = 0.0
        for card in itervalues(self.config['cards']['scored']['sections']):
            cases = card.get("cases", None)
            if cases is None:
                continue
            weight = card.get("weight", 1.0)
            card_score = scores.loc[cases, "score"].sum()
            card_total = scores.loc[cases, "max"].sum()
            card["score"] = card_score / card_total
            score += card_score * weight
            maximum += card_total * weight
        self.result["score"] = score / maximum
