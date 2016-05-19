#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability,
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
test_memote
----------------------------------

Tests for `memote` module.
"""

import os
import glob

from cameo import load_model

from memote import generate_memote_suite

TESTDIR = os.path.dirname(__file__)

models = [load_model(model, sanitize=False) for model in glob.glob(os.path.join(TESTDIR, 'data', '*.xml'))]

testsuite = generate_memote_suite(models)

if __name__ == "__main__":
    import nose
    nose.runmodule(config=nose.config.Config(verbosity=3))
