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

"""Provide a collective access to a test suite result.."""

from __future__ import absolute_import

import platform
from datetime import datetime

from depinfo import get_pkg_info


__all__ = ("MemoteResult",)


class MemoteResult(dict):
    """Collect the metabolic model test suite results."""

    def __init__(self, *args, **kwargs):
        """
        Instantiate a result structure.

        Parameters
        ----------
        args :
        kwargs :

        """
        super(MemoteResult, self).__init__(*args, **kwargs)
        self.meta = self.setdefault("meta", dict())
        self.cases = self.setdefault("tests", dict())

    @staticmethod
    def add_environment_information(meta):
        """Record environment information."""
        meta["timestamp"] = datetime.utcnow().isoformat(" ")
        meta["platform"] = platform.system()
        meta["release"] = platform.release()
        meta["python"] = platform.python_version()
        meta["packages"] = get_pkg_info("memote")
