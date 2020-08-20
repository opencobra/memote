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

import logging

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
        self._report_type = "snapshot"
        self.determine_miscellaneous_tests()
        self.compute_score()
        self.result.update(self.config)
