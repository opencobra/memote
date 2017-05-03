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

"""Render a basic one-time report."""

from __future__ import absolute_import

from memote.suite.reporting.reports.report import Report


class BasicReport(Report):
    """Render a basic report from the given data."""

    def __init__(self, data, **kwargs):
        """Initialize the data."""
        super(BasicReport, self).__init__(**kwargs)
        self.data = data

    def render_html(self):
        """Render a one-shot report for a model."""
        template = self.env.get_template("basic_report.html")
        return template.render(
            name=self.data["report"]["test_basic"]["model_id"],
            timestamp=self.data["meta"]["timestamp"],
            data=self.data)
