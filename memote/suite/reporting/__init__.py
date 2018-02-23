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
Subpackage for creating visually pleasing reports of test results.

There are three types of reports that we support:

1. A one-time report of a model giving a good insight into its current state.
2. A more elaborate report that makes use of the model development over time
   (aka git history).
3. A comparison report between two different versions of the same model or
   across different models (similar to a diff).
"""

from __future__ import absolute_import

from memote.suite.reporting.config import *
from memote.suite.reporting.snapshot import *
from memote.suite.reporting.history import *
from memote.suite.reporting.diff import *
