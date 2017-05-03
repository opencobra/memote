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

from jinja2 import Environment, PackageLoader, select_autoescape


class Report(object):
    """Render a model report."""

    def __init__(self, **kwargs):
        """Initialize the Jinja2 environment."""
        super(Report, self).__init__(**kwargs)
        self.env = Environment(
            loader=PackageLoader("memote.suite.reporting", "templates"),
            autoescape=select_autoescape(["html", "xml"])
        )

    def render_html(self):
        """Render an HTML report for a model."""
        raise NotImplementedError("Semi-abstract base class.")
