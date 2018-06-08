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

"""Compare two models with one another."""

from __future__ import absolute_import

from memote.suite.reporting.report import Report


class DiffReport(Report):
    """
    Render a report displaying the results of two or more models.

    Attributes
    ----------
    diff_results : python.Dictionary
        The dictionary structure of memote.MemoteResult objects.
    configuration : memote.MemoteConfiguration
        A memote configuration structure.

    """

    def __init__(self, diff_results, configuration, **kwargs):
        """Initialize the data."""
        super(DiffReport, self).__init__(
            result=None, configuration=configuration, **kwargs)
        self.results = diff_results
        self.config = configuration
        self._report_type = "diff"

    def render_html(self):
        """Render an HTML report for a model."""
        raise NotImplementedError(u"Coming soon™.")
