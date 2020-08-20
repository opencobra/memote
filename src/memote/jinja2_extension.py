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

"""Provide a jinja2 extension for the cookiecutter.."""

from __future__ import absolute_import

import os
from os.path import basename, expanduser, isabs, join

from jinja2.ext import Extension


__all__ = ("MemoteExtension",)


class MemoteExtension(Extension):
    """Provide an absolute path to a file."""

    tags = frozenset(["basename", "dirname", "abspath"])

    def __init__(self, environment):
        """Initialize the extension and prepare the jinja2 environment."""
        super(MemoteExtension, self).__init__(environment)
        environment.filters["normalize"] = self.normalize
        environment.filters["basename"] = basename

    @staticmethod
    def normalize(filename):
        """Return an absolute path of the given file name."""
        # Default value means we do not resolve a model file.
        if filename == "default":
            return filename
        filename = expanduser(filename)
        if isabs(filename):
            return filename
        else:
            return join(os.getcwd(), filename)
