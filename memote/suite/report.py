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
from builtins import dict

import dask
from jinja2 import Environment, PackageLoader, select_autoescape


class Report(object):
    """
    """

    def __init__(self, filename, data=None, **kwargs):
        """
        """
        super(Report, self).__init__(**kwargs)
        self.env = Environment(
            loader=PackageLoader("memote.suite", "templates"),
            autoescape=select_autoescape(["html", "xml"])
        )
        self.data = data


    def render_individual(self):
        """
        """
        template = self.env.get_template("individual.html")
        return template.render(
            name=self.data["report"]["memote.suite.test_basic"]["model_id"],
            timestamp=self.data["meta"]["timestamp"],
            data=self.data)

def render_diff():
    """
    """
    pass

def render_with_history():
    """
    """
    pass
