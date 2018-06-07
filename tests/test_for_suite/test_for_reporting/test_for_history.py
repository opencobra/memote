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


from memote.suite.api import test_model, history_report
from memote.suite.results import HistoryManager
from memote.suite.results import RepoResultManager
from memote.suite.reporting import (
    HistoryReport, ReportConfiguration)


@pytest.fixture(scope="session")
def mock_history_report(tmpdir_factory):
    """Build a mock git repository with two branches and one commit each."""
    # Initialize temporary directory
    repo_path = tmpdir_factory.mktemp("git_repo")
    # Create git repository on temporary directory.
    git_repo = Repo.init(repo_path)
    # Create mockup mini model.
    base = cobra.Model('mock model')
    met_a = cobra.Metabolite("A", name="A")
    met_b = cobra.Metabolite("B", name="B")
    rxn1 = cobra.Reaction("R1")
    rxn1.add_metabolites({met_a: -1, met_b: 1})
    base.add_reactions([rxn1])
    # Write mini model as SBML file to the temporary directory.
    model_path = str(repo_path.join('model.xml'))
    cobra.io.write_sbml_model(base, model_path)
    # Add and commit the file to the master branch of the mock repo.
    git_repo.index.add([model_path])
    git_repo.index.commit("initial commit")
    # Make a small change to the mockup model.
    met_c = cobra.Metabolite("C", name="C")
    rxn2 = cobra.Reaction("R2")
    rxn2.add_metabolites({met_b: -1, met_c: 1})
    base.add_reactions([rxn2])
    # Checkout and commit the changes to develop.
    git_repo.git.checkout('HEAD', b="develop")
    cobra.io.write_sbml_model(base, model_path)
    git_repo.index.add([str(model_path)])
    git_repo.index.commit("second commit")
    # Calculate the memote results for the commit history of the mockup repo.
    location = str(repo_path.join('Results'))
    manager = RepoResultManager(repository=git_repo, location=location)
    history = HistoryManager(repository=git_repo, manager=manager)
    history.build_branch_structure()
    for commit in history.iter_commits():
        git_repo.git.checkout(commit)
        model = cobra.io.read_sbml_model(model_path)
        _, result = test_model(model, results=True)
        manager.store(result, commit=commit)
    history.reset()
    # Return history report.
    json_report = history_report(git_repo, manager, html=False)
    return json_report


def test_structure(mock_history_report):
    """Expect this one thing to be true."""
    assert mock_history_report.keys() == ['cards', 'tests', 'score']
