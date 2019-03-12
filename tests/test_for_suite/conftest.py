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

from __future__ import absolute_import

import logging
from os import chdir, getcwd
from builtins import str
from os.path import basename, dirname, pardir, join
from shutil import copyfile
from git import Repo, InvalidGitRepositoryError
from tarfile import open

import pytest
from click.testing import CliRunner

LOGGER = logging.getLogger()


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(scope="session")
def model_file(small_file, tmpdir_factory):
    filename = str(tmpdir_factory.mktemp("small_models").join(
        basename(small_file)))
    copyfile(small_file, filename)
    return filename


@pytest.fixture(scope="session")
def invalid_file(invalid_model, tmpdir_factory):
    filename = str(tmpdir_factory.mktemp("invalid_models").join(
        basename(invalid_model)))
    copyfile(invalid_model, filename)
    return filename


@pytest.fixture(scope="function")
def mock_repo(tmpdir_factory):
    """
    Unzips the mock repo providing the path to it and a repo instance.

    """
    cwd = getcwd()
    # Define the path to the temporary folder
    base_path = str(tmpdir_factory.mktemp("mock-repo"))
    # and the tarball that we will decompress there
    tar_file = join(
        dirname(__file__), pardir, "data", "memote-mock-repo.tar.gz"
    )
    # Extract the gzipped tarball
    mock_repo_tarfile = open(tar_file)
    mock_repo_tarfile.extractall(base_path)
    mock_repo_tarfile.close()
    # Obtain the repository as a gitpython Repo object
    path = join(base_path,"memote-mock-repo")
    chdir(path)
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        LOGGER.warning(
            "Could not find memote-mock-repository. Is the path correct?")
    chdir(cwd)
    return path, repo
