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
from os.path import join
from string import Template
# from zlib import compress

from memote.utils import log_json_incompatible_types
from memote.suite.reporting import TEMPLATES_PATH
from memote.suite.reporting.report import Report

LOGGER = logging.getLogger(__name__)


class SnapshotReport(Report):
    """Render a one-time report from the given model results."""

    def __init__(self, **kwargs):
        """Initialize the data."""
        super(SnapshotReport, self).__init__(**kwargs)
        with open(
            join(TEMPLATES_PATH, "index.html"), encoding="utf-8"
        ) as file_path:
            self._template = Template(file_path.read())

    def render_html(self):
        """Render the snapshot report by writing JSON into the template."""
        self.determine_miscellaneous_tests()
        self.compute_score()
        self.result.store.update(self.config)
        try:
            return self._template.safe_substitute(
                results=json.dumps(self.result.store, sort_keys=False,
                                   indent=None, separators=(",", ":")))
        except TypeError:
            log_json_incompatible_types(self.result.store)

        # TODO: Use compression of JSON in future.
        # return template.safe_substitute(
        #     results=b64encode(compress(
        #         json.dumps(self.data).encode("UTF-16"), level=9)))
        # return template.render(
        #     result=Markup(b64encode(
        #       compress(json.dumps(self.data), level=9))))
