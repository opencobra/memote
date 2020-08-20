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

"""Configure the layout and scoring of test reports."""

from __future__ import absolute_import

import logging
from builtins import open

from importlib_resources import open_text
from ruamel.yaml import YAML

import memote.suite.templates as templates


__all__ = ("ReportConfiguration",)

LOGGER = logging.getLogger(__name__)
yaml = YAML(typ="safe")


class ReportConfiguration(dict):
    """Collect the metabolic model test suite results."""

    def __init__(self, *args, **kwargs):
        """
        Instantiate a configuration structure.

        Parameters
        ----------
        args :
        kwargs :

        """
        super(ReportConfiguration, self).__init__(*args, **kwargs)

    @classmethod
    def load(cls, filename=None):
        """Load a test report configuration."""
        if filename is None:
            LOGGER.debug("Loading default configuration.")
            with open_text(
                templates, "test_config.yml", encoding="utf-8"
            ) as file_handle:
                content = yaml.load(file_handle)
        else:
            LOGGER.debug("Loading custom configuration '%s'.", filename)
            try:
                with open(filename, encoding="utf-8") as file_handle:
                    content = yaml.load(file_handle)
            except IOError as err:
                LOGGER.error(
                    "Failed to load the custom configuration '%s'. Skipping.", filename
                )
                LOGGER.debug(str(err))
                content = dict()
        return cls(content)

    def merge(self, other):
        """Merge a custom configuration."""
        self.update(other)
