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


import json
import logging

from goodtables import validate
from importlib_resources import open_text

# Importing the checks is necessary in order to register them.
import memote.experimental.schemata
from memote.experimental.checks import UnknownIdentifier  # noqa: F401
from memote.experimental.tabular import read_tabular


__all__ = ("ExperimentalBase",)


LOGGER = logging.getLogger(__name__)


class ExperimentalBase(object):
    """Represent a specific medium condition."""

    SCHEMA = None
    TRUTHY = {"true", "True", "TRUE", "1", "yes", "Yes", "YES"}

    def __init__(self, identifier, obj, filename, **kwargs):
        """
        Initialize a medium.

        Parameters
        ----------
        identifier : str
        obj : dict
        filename : str or pathlib.Path
            The full file path. May be a compressed file.
        kwargs

        """
        super(ExperimentalBase, self).__init__(**kwargs)
        self.id = identifier
        self.label = obj.get("label")
        if self.label is None:
            self.label = ""
        self.filename = filename
        self.data = None
        self.schema = None

    def load(self, dtype_conversion=None):
        """
        Load the data table and corresponding validation schema.

        Parameters
        ----------
        dtype_conversion : dict
            Column names as keys and corresponding type for loading the data.
            Please take a look at the `pandas documentation
            <https://pandas.pydata.org/pandas-docs/stable/io.html#specifying-column-data-types>`__
            for detailed explanations.

        """
        self.data = read_tabular(self.filename, dtype_conversion)
        with open_text(
            memote.experimental.schemata, self.SCHEMA, encoding="utf-8"
        ) as file_handle:
            self.schema = json.load(file_handle)

    def validate(self, model, checks=None):
        """Use a defined schema to validate the given table."""
        if checks is None:
            checks = []
        records = self.data.to_dict("records")
        self.evaluate_report(
            validate(
                records,
                headers=list(records[0]),
                preset="table",
                schema=self.schema,
                order_fields=True,
                checks=checks,
            )
        )

    @staticmethod
    def evaluate_report(report):
        """Iterate over validation errors."""
        if report["valid"]:
            return
        for warn in report["warnings"]:
            LOGGER.warning(warn)
        # We only ever test one table at a time.
        for err in report["tables"][0]["errors"]:
            LOGGER.error(err["message"])
        raise ValueError("Invalid data file. Please see errors above.")
