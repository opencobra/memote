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
from os.path import join
from shutil import rmtree
from subprocess import check_output, call
from tempfile import mkdtemp
import tarfile

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger()

def update_mock_repo():
    """
    Clone and gzip the memote-mock-repo used for CLI and integration tests.

    The repo is hosted at
    'https://github.com/ChristianLieven/memote-mock-repo.git' and maintained
    separately from

    """
    target_file = os.path.abspath(
        join("tests", "data", "memote-mock-repo.tar.gz")
    )
    temp_dir = mkdtemp(prefix='tmp_mock')
    previous_wd = os.getcwd()
    try:
        LOGGER.info("Cloning repository.")
        os.chdir(temp_dir)
        check_output(
            ['git', 'clone',
             'https://github.com/ChristianLieven/memote-mock-repo.git']
        )
        os.chdir('memote-mock-repo/')
        LOGGER.info("Setting git to ignore filemode changes.")
        call(
            ['git', 'config',
             'core.fileMode', 'false']
        )
        call(
            ['git', 'config',
             'user.email', 'memote@opencobra.com']
        )
        call(
            ['git', 'config',
             'user.name', 'memote-bot']
        )
    finally:
        LOGGER.info("Compressing to tarball.")
        tar = tarfile.open(target_file, "w:gz")
        tar.add(
            join(temp_dir, 'memote-mock-repo/'),
            arcname="memote-mock-repo"
        )
        tar.close()
        LOGGER.info("Success!")
        LOGGER.info("Removing temporary directory.")
        rmtree(temp_dir)
        LOGGER.info("Success! The mock repo has been updated.")
        os.chdir(previous_wd)


if __name__ == "__main__":
    update_mock_repo()
