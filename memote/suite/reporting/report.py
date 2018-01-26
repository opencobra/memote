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

from six import iteritems, itervalues


class Report(object):
    """Determine the abstract report interface."""

    def __init__(self, result, configuration):
        """
        Fuse a collective result with a report configuration.

        Parameters
        ----------
        result : memote.MemoteResult
        configuration : memote.MemoteConfiguration

        """
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
            cases = card.get("cases", [])
            tests_on_cards.update(cases)
        # Add all other tests.
        for card, content in iteritems(self.config["cards"]):
            if card == "scored":
                continue
            cases = content.get("cases", [])
            tests_on_cards.update(cases)

        self.config["cards"].setdefault("misc", dict())
        self.config["cards"]["misc"]["title"] = "Misc. Tests"
        self.config["cards"]["misc"]["cases"] = list(
            set(self.result["tests"]) - set(tests_on_cards))

