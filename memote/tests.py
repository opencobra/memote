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

__all__ = ['generate_memote_suite']

from functools import partial

from memote.util import metabolites_without_formula


def check_has_reactions_attr(model):
    assert hasattr(model, 'reactions')

def check_all_metabolites_have_formulas(model):
    assert len(metabolites_without_formula(model)) == 0

def test_wrapper(test, model):
    func = partial(test, model)
    func.description = '{} {}'.format(func.func.__name__, model.id)
    return func

def generate_memote_suite(models):
    def testsuite():
        for model in models:
            yield test_wrapper(check_has_reactions_attr, model)
            yield test_wrapper(check_all_metabolites_have_formulas, model)

    return testsuite
