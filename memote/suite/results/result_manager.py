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

import json
import logging
import platform
from builtins import open
from datetime import datetime

from depinfo import get_pkg_info
from future.utils import raise_with_traceback

from memote.utils import log_json_incompatible_types
from memote.suite.results.result import MemoteResult

__all__ = ("ResultManager",)

LOGGER = logging.getLogger(__name__)


class ResultManager(object):
    """Manage storage of results to JSON files."""

    def __init__(self, **kwargs):
        """Initialize a JSON file storage manager."""
        super(ResultManager, self).__init__(**kwargs)

    @staticmethod
    def add_environment(meta):
        """Record environment information."""
        meta["timestamp"] = datetime.utcnow().isoformat(" ")
        meta["platform"] = platform.system()
        meta["release"] = platform.release()
        meta["python"] = platform.python_version()
        meta["packages"] = get_pkg_info("memote")

    def store(self, result, filename, env_info=True, pretty=True):
        """
        Write a result to the given file.

        Parameters
        ----------
        result : memote.MemoteResult
            The dictionary structure of results.
        filename : str or pathlib.Path
            Store results directly to the given filename.
        env_info : bool, optional
            Add Python environment information to the result object.
        pretty : bool, optional
            Whether (default) or not to write JSON in a more legible format.

        """
        if env_info:
            self.add_environment(result.meta)
        if pretty:
            kwargs = dict(sort_keys=True, indent=2,
                          separators=(",", ": "), ensure_ascii=False)
        else:
            kwargs = dict(sort_keys=False, indent=None,
                          separators=(",", ":"), ensure_ascii=False)
        LOGGER.info("Storing result in '%s'.", filename)
        with open(filename, "w", encoding="utf-8") as file_handle:
            try:
                return file_handle.write(json.dumps(result, **kwargs))
            except TypeError as error:
                log_json_incompatible_types(result)
                raise_with_traceback(error)

    def load(self, filename):
        """Load a result from the given JSON file."""
        # TODO: validate the read-in JSON maybe?
        LOGGER.info("Loading result from '%s'.", filename)
        with open(filename, encoding="utf-8") as file_handle:
            result = MemoteResult(json.load(file_handle))
        return result
