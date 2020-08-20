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

"""Provide the memote result managers for various storage backends."""

from __future__ import absolute_import

import gzip
import json
import logging
from builtins import open

from memote.suite.results.result import MemoteResult
from memote.utils import jsonify


__all__ = ("ResultManager",)

LOGGER = logging.getLogger(__name__)


class ResultManager(object):
    """Manage storage of results to JSON files."""

    def __init__(self, **kwargs):
        """Initialize a JSON file storage manager."""
        super(ResultManager, self).__init__(**kwargs)

    def store(self, result, filename, pretty=True):
        """
        Write a result to the given file.

        Parameters
        ----------
        result : memote.MemoteResult
            The dictionary structure of results.
        filename : str or pathlib.Path
            Store results directly to the given filename.
        pretty : bool, optional
            Whether (default) or not to write JSON in a more legible format.

        """
        LOGGER.info("Storing result in '%s'.", filename)
        if filename.endswith(".gz"):
            with gzip.open(filename, "wb") as file_handle:
                file_handle.write(jsonify(result, pretty=pretty).encode("utf-8"))
        else:
            with open(filename, "w", encoding="utf-8") as file_handle:
                file_handle.write(jsonify(result, pretty=pretty))

    def load(self, filename):
        """Load a result from the given JSON file."""
        LOGGER.info("Loading result from '%s'.", filename)
        if filename.endswith(".gz"):
            with gzip.open(filename, "rb") as file_handle:
                result = MemoteResult(json.loads(file_handle.read().decode("utf-8")))
        else:
            with open(filename, "r", encoding="utf-8") as file_handle:
                result = MemoteResult(json.load(file_handle))
        # TODO (Moritz Beber): Validate the read-in JSON maybe? Trade-off
        #  between extra time taken and correctness. Maybe we re-visit this
        #  issue when there was a new JSON format version needed.
        return result
