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

from memote.suite.results.result import MemoteResult
from memote.suite.results.repo_result_manager import RepoResultManager
from memote.suite.results.models import Result, Base

__all__ = ("SQLResultManager",)

LOGGER = logging.getLogger(__name__)

Session = sessionmaker()


class SQLResultManager(RepoResultManager):
    """Manage storage of results to a database."""

    def __init__(self, **kwargs):
        """
        Initialize the repository aware database storage manager.

        Parameters
        ----------
        location : str
            A Database connection URL.

        """
        super(SQLResultManager, self).__init__(**kwargs)
        self._backend = create_engine(self._backend)
        # Create the database and tables if it doesn't exist.
        Base.metadata.create_all(self._backend, checkfirst=True)
        self.session = Session(bind=self._backend)

    def store(self, result, commit=None, **kwargs):
        """
        Store a result in a JSON file attaching git meta information.

        Parameters
        ----------
        result : memote.MemoteResult
            The dictionary structure of results.
        commit : str, optional
            Unique hexsha of the desired commit.
        kwargs :
            Passed to parent function.

        """
        git_info = self.record_git_info(commit)
        try:
            row = self.session.query(Result). \
                filter_by(hexsha=git_info.hexsha). \
                one()
            LOGGER.info("Updating result '%s'.", git_info.hexsha)
            row.memote_result = result
        except NoResultFound:
            row = Result(memote_result=result)
            LOGGER.info("Storing result '%s'.", git_info.hexsha)
        row.hexsha = git_info.hexsha
        row.author = git_info.author
        row.email = git_info.email
        row.authored_on = git_info.authored_on
        self.session.add(row)
        self.session.commit()

    def load(self, commit=None):
        """Load a result from the database."""
        git_info = self.record_git_info(commit)
        LOGGER.info("Loading result from '%s'.", git_info.hexsha)
        result = MemoteResult(
            self.session.query(Result.memote_result).
            filter_by(hexsha=git_info.hexsha).
            one().memote_result)
        # Add git info so the object is equivalent to the one returned by the
        #  RepoResultManager.
        self.add_git(result.meta, git_info)
        return result
