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
from typing import Optional

import pandera as pa
from pandera.typing import Series

from memote.experimental.experimental_base import ExperimentalBase


__all__ = ("Medium",)

LOGGER = logging.getLogger(__name__)


class MediumModel(pa.DataFrameModel):
    exchange: Series[str] = pa.Field(
        description="The exchange reaction identifiers must correspond to the "
        "metabolic model identifiers.",
        title="Exchange Reaction Identifier",
        unique=True,
    )
    uptake: Series[float] = pa.Field(
        ge=0.0,
        le=1000.0,
        title="Uptake Rate",
        description="The uptake rate for the exchange reaction. For models following "
        "common practices this modifies the lower bound.",
    )
    comment: Optional[Series[str]] = pa.Field(
        nullable=True,
        title="Comment",
        description="Optional comment which is not processed further.",
    )

    class Config:
        coerce = True
        strict = "filter"


class Medium(ExperimentalBase):
    """Represent a specific medium condition."""

    def __init__(self, **kwargs):
        """
        Initialize a medium.

        Parameters
        ----------
        kwargs

        """
        super(Medium, self).__init__(**kwargs)

    def validate(self, model):
        """Use a defined schema to validate the medium table format."""
        MediumModel.validate(self.data, lazy=True)
        assert self.data["exchange"].isin({r.id for r in model.reactions}).all()

    def apply(self, model):
        """Set the defined medium on the given model."""
        model.medium = {
            row.exchange: row.uptake for row in self.data.itertuples(index=False)
        }
