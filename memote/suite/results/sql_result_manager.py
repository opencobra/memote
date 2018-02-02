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

"""Provide the memote result managers for various storage backends."""

from __future__ import absolute_import

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from memote.suite.results.result_manager import ResultManager
from memote.suite.results.models import Result, Base

LOGGER = logging.getLogger(__name__)

Session = sessionmaker()


class SQLResultManager(ResultManager):

    def __init__(self, connector, **kwargs):
        """

        Parameters
        ----------
        connector : str
            Database connection string.

        """
        super(ResultManager, self).__init__(**kwargs)
        self.backend = create_engine(connector)
        # Create the database and tables if it doesn't exist.
        Base.metadata.create_all(self.backend, checkfirst=True)
        self.session = Session(bind=self.backend)

    def store(self, result, repo=None, commit=None, filename=None):
        """
        Safe a result to the chosen backend attaching git information.

        Parameters
        ----------
        result : memote.MemoteResult
        repo : git.Repo, optional
        commit : str, optional
            Unique hexsha of the desired commit.
        filename : str, optional
            Filename argument is ignored for SQL backend.

        """
        result = Result(results=result.store)
        if repo is not None:
            git_info = self.record_git_info(repo, commit)
            result.hexsha = git_info.hexsha,
            result.author = git_info.author
            result.email = git_info.email
            result.authored_on = git_info.authored_on
        self.session.add(result)
        self.session.commit()
