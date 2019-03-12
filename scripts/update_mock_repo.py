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
from os.path import dirname, join, pardir
from shutil import rmtree
from git import Repo
from tempfile import mkdtemp
import tarfile

LOGGER = logging.getLogger()


def update_mock_repo():
    """
    Clone and gzip the memote-mock-repo used for CLI and integration tests.

    The repo is hosted at
    'https://github.com/ChristianLieven/memote-mock-repo.git' and maintained
    separately from

    """
    target_file = join(
        dirname(__file__), pardir, "tests", "data", "memote-mock-repo.tar.gz"
    )
    temp_dir = mkdtemp(prefix='tmp_mock')
    try:
        LOGGER.info("Cloning repository.")
        Repo.clone_from(
            'https://github.com/ChristianLieven/memote-mock-repo.git',
            temp_dir)
    finally:
        LOGGER.info("Compressing to tarball.")
        tar = tarfile.open(target_file, "w:gz")
        tar.add(temp_dir, arcname="memote-mock-repo")
        tar.close()
        LOGGER.info("Success!")
        LOGGER.info("Removing temporary directory.")
        rmtree(temp_dir)
        LOGGER.info("Success! The mock repo has been updated.")


if __name__ == "__main__":
    update_mock_repo()