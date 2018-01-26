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

import pip

from memote.version_info import PKG_ORDER


class MemoteResult(object):
    """Collect the metabolic model test suite results."""

    def __init__(self, **kwargs):
        """"""
        super(MemoteResult, self).__init__(**kwargs)
        self.store = dict()
        self.store["meta"] = self.meta = dict()
        self.store["tests"] = self.cases = dict()

    def record_environment(self):
        """Record environment information."""
        self.meta["timestamp"] = datetime.utcnow().isoformat(" ")
        self.meta["platform"] = platform.system()
        self.meta["release"] = platform.release()
        self.meta["python"] = platform.python_version()
        dependencies = frozenset(PKG_ORDER)
        self.meta["packages"] = dict(
            (dist.project_name, dist.version) for dist in
            pip.get_installed_distributions()
            if dist.project_name in dependencies)

