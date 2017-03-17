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

try:
    import simplejson as json
except ImportError:
    import json
from os.path import join

import dask.bag as db
from jinja2 import Environment, PackageLoader, select_autoescape


class Report(object):
    """Render a basic report from the given data."""

    def __init__(self, data=None, **kwargs):
        """Initialize the Jinja2 environment and data."""
        super(Report, self).__init__(**kwargs)
        self.env = Environment(
            loader=PackageLoader("memote.suite", "templates"),
            autoescape=select_autoescape(["html", "xml"])
        )
        self.data = data

    def render_html(self):
        """Render a one-shot report for a model."""
        template = self.env.get_template("basic.html")
        return template.render(
            name=self.data["report"]["memote.suite.test_basic"]["model_id"],
            timestamp=self.data["meta"]["timestamp"],
            data=self.data)


class GitEnabledReport(Report):
    """Render a rich report using the git repository history."""

    def __init__(self, repo, directory, **kwargs):
        """Initialize the Jinja2 environment and data."""
        super(GitEnabledReport, self).__init__(**kwargs)
        self.repo = repo
        self.latest = self.repo.active_branch.commit
        self.bag = self._collect_bag()

    def render_html(self):
        """Render a rich report for the repository."""
        template = self.env.get_template("git_enabled.html")
        return template.render(
            name=self.data["report"]["memote.suite.test_basic"]["model_id"],
            timestamp=self.data["meta"]["timestamp"],
            data=self.data)

    def _collect_bag(self):
        """Collect all data into a dask bag."""
        files = [join(self.directory, "{}.json".format(commit.hexsha))
                 for commit in self.latest.iter_parents()]
        return db.read_text(files).map(json.loads)


