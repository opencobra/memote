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

"""Custom checks for `goodtables`."""

from __future__ import absolute_import

from goodtables import Error, check


@check("unknown-identifier", type="custom", context="body")
class UnknownIdentifier:
    """
    Validate data identifiers against a known set.

    Attributes
    ----------
    column : str
        The header of the data column to check.
    identifiers : iterable of str
        The known set of identifiers.

    """

    def __init__(self, column, identifiers, **_):
        """
        Initialize the custom identfier check.

        Parameters
        ----------
        column : str
            The header of the data column to check.
        identifiers : iterable of str
            The known set of identifiers.

        """
        self.column = column
        self.identifiers = frozenset(identifiers)

    def check_row(self, cells):
        """Check each row in the data table."""
        cell = None
        for item in cells:
            if item["header"] == self.column:
                cell = item
                break

        if cell is None:
            error = Error(
                "unknown-identifier",
                row_number=cells[0]["row-number"],
                message="Checking identifiers requires the column "
                "'{column}' to exist.".format(column=self.column),
            )
            return [error]

        value = cell.get("value")
        if value not in self.identifiers:
            error = Error(
                "unknown-identifier",
                cell,
                message="Value '{value}' in column {header} on row "
                "{row_number} is an unknown identifier.",
                message_substitutions={"value": value},
            )
            return [error]
