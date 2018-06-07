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

"""Ensure the expected functioning of ``memote.suite.reporting.history``."""

from __future__ import absolute_import

from os.path import exists
from builtins import str

import cobra
from git import Repo
import pytest

import memote.suite.reporting.history as history
from memote.utils import register_with

@pytest.fixture(scope="session")
def mock_repo(tmpdir_factory):
    """Build a mock git repository with two branches and one commit each."""
    repo_path = tmpdir_factory.mktemp("git_repo")
    git_repo = Repo.init(repo_path, bare=True)
    return git_repo

