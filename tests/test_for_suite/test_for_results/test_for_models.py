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

"""Test the expected behavior of database persistence."""

from __future__ import absolute_import

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

import memote.suite.results.models as models

Session = sessionmaker()


@pytest.fixture(scope="module", params=["memory", "disk"])
def storage(request, tmpdir_factory):
    if request.param == "disk":
        store = str(tmpdir_factory.mktemp("sqlite").join("test.db"))
    else:
        store = ":memory:"
    return "sqlite:///{}".format(store)


@pytest.fixture(scope="module")
def connection(storage):
    """
    Use a connection such transactions can be used.

    Notes
    -----
    Follows a transaction pattern described in the following:
    http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#session-begin-nested
    """
    engine = create_engine(storage)
    models.Base.metadata.create_all(engine)
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope="function")
def session(connection):
    """
    Create a transaction and session per test unit.

    Rolling back a transaction removes even committed rows
    (``session.commit``) from the database.
    """
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()


class TestResult(object):

    def test_create(self):
        timestamp = datetime.now()
        commit = models.Result(
            hexsha="abcdef",
            authored_on=timestamp,
            memote_result={"foo": "bar"}
        )
        assert commit.hexsha == "abcdef"
        assert commit.authored_on == timestamp
        assert commit.memote_result == {"foo": "bar"}

    def test_insert(self, session):
        timestamp = datetime.now()
        commit = models.Result(
            hexsha="abcdef",
            authored_on=timestamp,
            memote_result={"foo": "bar"}
        )
        session.add(commit)
        session.commit()
        assert commit.id is not None
        results = session.query(models.Result).all()
        assert len(results) == 1
        assert results[0] == commit

    @pytest.mark.parametrize("name_a, name_b", [
        ("abcdef", "ghijkl"),
        pytest.param("same", "same",
                     marks=pytest.mark.raises(exception=IntegrityError))
    ])
    def test_unique_hexsha(self, session, name_a, name_b):
        timestamp = datetime.now()
        commit_a = models.Result(
            hexsha=name_a,
            authored_on=timestamp,
            memote_result={"foo": "bar"}
        )
        commit_b = models.Result(
            hexsha=name_b,
            authored_on=timestamp,
            memote_result={"foo": "bar"}
        )
        session.add_all([commit_a, commit_b])
        session.commit()
