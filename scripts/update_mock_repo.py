# -*- coding: utf-8 -*-

# Copyright 2019 Novo Nordisk Foundation Center for Biosustainability,
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

"""
Update the mock repo that is used for the memote CLI and integration tests.

Dependencies are assumed to be satisfied by having memote installed in the
same project.

"""

from __future__ import absolute_import

import logging
import os
import tarfile
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp

import git

LOGGER = logging.getLogger()


def update_mock_repo(temp_dir):
    """
    Clone and gzip the memote-mock-repo used for CLI and integration tests.

    The repo is hosted at
    'https://github.com/ChristianLieven/memote-mock-repo.git' and maintained
    separately from

    """
    target_file = os.path.abspath(
        join("tests", "data", "memote-mock-repo.tar.gz")
    )
    repo_dir = join(temp_dir, 'memote-mock-repo')
    LOGGER.info("Cloning repository.")
    repo = git.Repo.clone_from(
        'https://github.com/ChristianLieven/memote-mock-repo.git',
        repo_dir
    )
    LOGGER.info("Setting git to ignore filemode changes.")
    with repo.config_writer() as writer:
        writer.set_value("core", "fileMode", "false").release()
        writer.set_value("user", "name", "memote-bot").release()
        writer.set_value("user", "email", "bot@memote.io").release()
    LOGGER.info("Compressing to tarball.")
    with tarfile.open(target_file, "w:gz") as archive:
        archive.add(
            repo_dir,
            arcname="memote-mock-repo"
        )
    LOGGER.info("Success! The mock repo has been updated.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s"
    )
    temp_dir = mkdtemp(prefix='tmp_mock')
    try:
        update_mock_repo(temp_dir)
    finally:
        LOGGER.info("Removing temporary directory.")
        rmtree(temp_dir)
