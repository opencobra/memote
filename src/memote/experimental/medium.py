# -*- coding: utf-8 -*-

# Copyright 2018 Novo Nordisk Foundation Center for Biosustainability,
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

"""Provide a class for medium definitions."""

from __future__ import absolute_import

import logging

from memote.experimental.experimental_base import ExperimentalBase


__all__ = ("Medium",)

LOGGER = logging.getLogger(__name__)


class Medium(ExperimentalBase):
    """Represent a specific medium condition."""

    SCHEMA = "medium.json"

    def __init__(self, **kwargs):
        """
        Initialize a medium.

        Parameters
        ----------
        kwargs

        """
        super(Medium, self).__init__(**kwargs)

    def validate(self, model, checks=None):
        """Use a defined schema to validate the medium table format."""
        if checks is None:
            checks = []
        custom = [
            {
                "unknown-identifier": {
                    "column": "exchange",
                    "identifiers": {r.id for r in model.reactions},
                }
            }
        ]
        super(Medium, self).validate(model=model, checks=checks + custom)

    def apply(self, model):
        """Set the defined medium on the given model."""
        model.medium = {
            row.exchange: row.uptake for row in self.data.itertuples(index=False)
        }
