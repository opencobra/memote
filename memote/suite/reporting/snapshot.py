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

"""Render a one-time model report."""

from __future__ import absolute_import

import json
import logging
# from base64 import b64encode
from string import Template
# from zlib import compress

from importlib_resources import read_text

import memote.suite.templates as templates
from memote.utils import log_json_incompatible_types
from memote.suite.reporting.report import Report

LOGGER = logging.getLogger(__name__)


class SnapshotReport(Report):
    """
    Render a one-time report from the given model results.

    Attributes
    ----------
    result : memote.MemoteResult
        The dictionary structure of results.
    configuration : memote.MemoteConfiguration
        A memote configuration structure.

    """

    def __init__(self, **kwargs):
        """Initialize the snapshot report."""
        super(SnapshotReport, self).__init__(**kwargs)
        self._template = Template(
            read_text(templates, "index.html", encoding="utf-8"))

    def render_html(self):
        """Render the snapshot report."""
        self.determine_miscellaneous_tests()
        self.compute_score()
        self.result.update(self.config)
        try:
            return self._template.safe_substitute(
                report_type="snapshot",
                results=json.dumps(self.result, sort_keys=False,
                                   indent=None, separators=(",", ":")))
        except TypeError:
            log_json_incompatible_types(self.result)

        # TODO: Use compression of JSON in future.
        # return template.safe_substitute(
        #     results=b64encode(compress(
        #         json.dumps(self.data).encode("UTF-16"), level=9)))
        # return template.render(
        #     result=Markup(b64encode(
        #       compress(json.dumps(self.data), level=9))))
