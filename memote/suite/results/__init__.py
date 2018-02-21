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

"""
Provide the memote result object and managers for various situations.

* The ``MemoteResult` represents the collective result of running the
  metabolic model test suite on a given model at a certain point in time.
* The ``ResultManager`` and its subclasses knows how to store a
``MemoteResult`` in various data backends (file, SQL, NoSQL).
* The ``ResultHistoryManager`` uses the different ``ResultManager``s to
  iterate over and collect a model's test result history.

"""

from __future__ import absolute_import

from memote.suite.results.result import *
from memote.suite.results.result_manager import *
from memote.suite.results.repo_result_manager import *
from memote.suite.results.sql_result_manager import *
from memote.suite.results.history_manager import *
