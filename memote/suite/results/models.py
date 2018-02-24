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

"""Persist the memote test suite results in a database."""

from __future__ import absolute_import

import json
import logging

from future.utils import raise_with_traceback
from sqlalchemy import Column, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base

from memote.utils import log_json_incompatible_types

__all__ = ("Result",)

LOGGER = logging.getLogger(__name__)

Base = declarative_base()


class JSON(TypeDecorator):
    """
    Implement a JSON column type.

    Most SQL databases now implement JSON blobs but unfortunately, SQLite
    only provides this via a compiled extension. So we encode to and decode
    from JSON in a normal text column.
    """

    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        """Convert the value to a JSON encoded string before storing it."""
        try:
            return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        except TypeError as error:
            log_json_incompatible_types(value)
            raise_with_traceback(error)

    def process_result_value(self, value, dialect):
        """Convert a JSON encoded string to a dictionary structure."""
        if value is not None:
            value = json.loads(value)
        return value


class Result(Base):
    """
    Model a git based result for storage in a database.

    The class attributes correspond both to the columns in the database table
    and to instance attributes.
    """

    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    hexsha = Column(Unicode(40), nullable=True, unique=True, index=True)
    author = Column(Unicode(255), nullable=True)
    email = Column(Unicode(255), nullable=True)
    authored_on = Column(DateTime(), nullable=True)
    memote_result = Column(JSON(), nullable=False)
