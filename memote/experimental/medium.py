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

from numpy import isfinite

from memote.experimental.experimental_base import ExperimentalBase
from memote.experimental.checks import check_partial, reaction_id_check

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

    def validate(self, model, checks=[]):
        """Use a defined schema to validate the medium table format."""
        custom = [
            check_partial(reaction_id_check,
                          frozenset(r.id for r in model.reactions))
        ]
        super(Medium, self).validate(model=model, checks=checks + custom)

    def apply(self, model):
        """Set the defined medium on the given model."""
        for rxn in model.exchanges:
            rxn.lower_bound = 0
        for row in self.data.itertuples(index=False):
            rxn = model.reactions.get_by_id(row.reaction)
            if isfinite(row.lower):
                rxn.lower_bound = row.lower
            if isfinite(row.upper):
                rxn.upper_bound = row.upper
