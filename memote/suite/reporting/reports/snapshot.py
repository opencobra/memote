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

import io
import json
import logging
# from base64 import b64encode
from string import Template
from os.path import join, dirname
# from zlib import compress

from six import iteritems

from memote.suite.reporting.reports.report import Report

LOGGER = logging.getLogger(__name__)


class SnapshotReport(Report):
    """Render a basic report from the given data."""

    def __init__(self, data, **kwargs):
        """Initialize the data."""
        super(SnapshotReport, self).__init__(**kwargs)
        self.data = data

    def render_html(self):
        """
        Render a one-shot report for a model.

        This is currently a stub while we convert from ``jinja2`` templates
        to a full Angular based report.
        """
        # template = self.env.get_template("snapshot.html")
        with io.open(join(dirname(__file__), "../templates/snapshot.html")) as \
                file_handle:
            template = Template(file_handle.read())
        try:
            return template.safe_substitute(
                results=json.dumps(self.data, sort_keys=True, indent=2,
                                   separators=(",", ": ")))
        except TypeError:
            # Log information to easily find the culprit.
            json_types = (type(None), int, float, str, list, dict)
            for name, annotation in iteritems(self.data["tests"]):
                data = annotation.get("data")
                try:
                    for key, value in iteritems(data):
                        if not isinstance(value, json_types):
                            LOGGER.debug(
                                "  %s - %s: %s", name, key, type(
                                    value)
                            )
                except AttributeError:
                    if not isinstance(data, json_types):
                        LOGGER.debug("  %s: %s", name, type(data))

        # TODO: Use compression of JSON in future.
        # return template.safe_substitute(
        #     results=b64encode(compress(
        #         json.dumps(self.data).encode("UTF-16"), level=9)))
        # return template.render(
        #     result=Markup(b64encode(
        #       compress(json.dumps(self.data), level=9))))
