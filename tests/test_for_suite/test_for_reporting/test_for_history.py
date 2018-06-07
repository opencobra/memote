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

def mock_model(base):
    met_a = cobra.Metabolite("A")
    met_b = cobra.Metabolite("B")
    rxn1 = cobra.Reaction("R1")
    rxn1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn1])
    return base

@pytest.mark.parametrize("model", [
    ("mock_repo"),
], indirect=["model"])
@pytest.fixture(scope="session")
def mock_repo(tmpdir_factory, model):
    """Build a mock git repository with two branches and one commit each."""
    repo_path = tmpdir_factory.mktemp("git_repo")
    git_repo = Repo.init(repo_path)
    cobra.io.write_sbml_model(model,repo_path.join('model.xml'))
    git_repo.index.add([repo_path.join('model.xml')])
    git_repo.index.commit("initial commit")
    met_c = cobra.Metabolite("C")
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({met_b: -1, met_c: 1})
    model.add_reactions([rxn2])
    git_repo.git.checkout('HEAD', b="develop")
    cobra.io.write_sbml_model(model,repo_path.join('model.xml'))
    git_repo.index.add([repo_path.join('model.xml')])
    git_repo.index.commit("second commit")
    return git_repo


@pytest.mark.parametrize("repo, num", [
    ("mock_repo", 0),
], indirect=["repo"])
def test_this_one_thing(repo, num):
    """Expect this one thing to be true."""
    print repo
    assert 0 == num
