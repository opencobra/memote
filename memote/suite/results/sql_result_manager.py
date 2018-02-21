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

"""Provide a memote result manager that is git aware and uses a SQL database."""

from __future__ import absolute_import

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from memote.suite.results.repo_result_manager import RepoResultManager
from memote.suite.results.models import Result, Base

__all__ = ("SQLResultManager",)

LOGGER = logging.getLogger(__name__)

Session = sessionmaker()


class SQLResultManager(RepoResultManager):

    def __init__(self, location, **kwargs):
        """

        Parameters
        ----------
        location : str
            A Database connection URL.

        """
        super(SQLResultManager, self).__init__(location=location, **kwargs)
        self.backend = create_engine(self.backend)
        # Create the database and tables if it doesn't exist.
        Base.metadata.create_all(self.backend, checkfirst=True)
        self.session = Session(bind=self.backend)

    def store(self, result, repo, commit=None, **kwargs):
        """
        Store a result in a SQL database attaching git meta information.

        Parameters
        ----------
        result : dict
            The dictionary structure of a memote.MemoteResult.
        repo : git.Repo, optional
        commit : str, optional
            Unique hexsha of the desired commit.
        kwargs :
            Ignored. Only exist to normalize function signature.

        """
        git_info = self.record_git_info(repo, commit)
        try:
            result = self.session.query(Result.results). \
                filter_by(hexsha=git_info.hexsha). \
                one()
            LOGGER.info("Updating result '%s'.", git_info.hexsha)
        except NoResultFound:
            result = Result(results=result)
            LOGGER.info("Storing result '%s'.", git_info.hexsha)
        result.hexsha = git_info.hexsha
        result.author = git_info.author
        result.email = git_info.email
        result.authored_on = git_info.authored_on
        self.session.add(result)
        self.session.commit()

    def load(self, repo, commit=None):
        """"""
        git_info = self.record_git_info(repo, commit)
        LOGGER.info("Loading result from '%s'.", git_info.hexsha)
        result = self.session.query(Result.results).\
            filter_by(hexsha=git_info.hexsha).\
            one()
        return result.results
