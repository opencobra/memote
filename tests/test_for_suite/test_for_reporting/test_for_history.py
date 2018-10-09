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

"""Ensure the expected functioning of ``memote.suite.reporting.history``."""

from __future__ import absolute_import

from six import iteritems

import pytest
from memote.suite.reporting import HistoryReport
from memote.suite.results.result import MemoteResult


MOCK_CONFIG_SCORES = {
        'cards': {
            'scored': {
                'sections': {
                    'scored_sub_section': {
                        'cases': [
                            'test_number',
                            'test_parametrized'
                        ],
                        'title': 'Scored Sub Section',
                        'weight': 1.0
                    }
                },
                'title': 'Core Tests'
            }
        },
        'weights': {
            'test_number': 1.0
        }
    }


MOCK_CONFIG = {
        'cards': {
            'scored': {
                'sections': {
                    'scored_sub_section': {
                        'cases': [
                            'test_parametrized'
                        ],
                        'title': 'Scored Sub Section',
                        'weight': 1.0
                    }
                },
                'title': 'Core Tests'
            },
            'test_basic': {
                'cases': [
                    'test_number'
                ],
                'title': 'Basic Information'
            }
        },
        'weights': {
            'test_number': 1.0,
            'test_parametrized': 1.0,
        }
    }


@pytest.fixture(scope="session")
def mock_history_manager():
    """Build a mock history manager that already contains results."""
    result1 = MemoteResult({
        "meta": {
            "branch": "master",
            "commit_author": "John Doe",
            "commit_hash": "3f4665356a24d76a9461043f62a2b12dab56c75f",
            "packages": {
                "SomePackage": "0.1.0"},
            "platform": "Darwin",
            "python": "2.7.10",
            "release": "14.5.0",
            "timestamp": "2017-05-03 18:26:11+02:00"
        },
        "tests": {
            "test_parametrized": {
                "data": {
                    "parameter1": ["item2", "item3"],
                    "parameter2": ["item4", "item3"]
                },
                "duration": {
                    "parameter1": 0.12,
                    "parameter2": 0.32
                },
                "format_type": 'percent',
                "message": {
                    "parameter1": "Some Message 1",
                    "parameter2": "Some Message 2"
                },
                "metric": {
                    "parameter1": 0.5,
                    "parameter2": 0.9
                },
                "result": {
                    "parameter1": "failed",
                    "parameter2": "failed"
                },
                "summary": "Some description of the test",
                "title": "Parametrized Test"
            },
            "test_number": {
                "data": ['x', 'y', 'z'],
                "duration": 0.002,
                "format_type": "count",
                "message": "Some Message 3",
                "result": "passed",
                "summary": "Some description again",
                "metric": 0.2,
                "title": "Non-Parametrized Test"
            }
        }
    })
    result2 = MemoteResult({
        "meta": {
            "branch": "develop",
            "commit_author": "John Doe",
            "commit_hash": "6e30d6236f5d47ebb4be39253eaa6a5dcb487687",
            "packages": {
                "SomePackage": "0.1.0"},
            "platform": "Darwin",
            "python": "2.7.10",
            "release": "14.5.0",
            "timestamp": "2017-05-03 18:50:11+02:00"
        },
        "tests": {
            "test_parametrized": {
                "data": {
                    "parameter1": ["item1", "item2"],
                    "parameter2": ["item2", "item3"]
                },
                "duration": {
                    "parameter1": 0.2,
                    "parameter2": 0.1
                },
                "format_type": 'percent',
                "message": {
                    "parameter1": "Some Message 1",
                    "parameter2": "Some Message 2"
                },
                "metric": {
                    "parameter1": 1.0,
                    "parameter2": 0.0
                },
                "result": {
                    "parameter1": "failed",
                    "parameter2": "failed"
                },
                "summary": "Some description of the test",
                "title": "Parametrized Test"
            },
            "test_number": {
                "data": ['x', 'y', 'z'],
                "duration": 0.002,
                "format_type": "count",
                "message": "Some Message 3",
                "result": "passed",
                "summary": "Some description again",
                "metric": 0.6,
                "title": "Non-Parametrized Test"
            }
        }
    })
    branch_structure = {
        "commits": {
            "3f4665356a24d76a9461043f62a2b12dab56c75f": {
                "timestamp": "2017-05-03 18:26:11+02:00",
                "author": "John Doe",
                "email": "John_Doe@test.com"
            },
            "6e30d6236f5d47ebb4be39253eaa6a5dcb487687": {
                "timestamp": "2017-05-03 18:50:11+02:00",
                "author": "John Doe",
                "email": "John_Doe@test.com"
            }
        },
        "branches": {
            "master": ["3f4665356a24d76a9461043f62a2b12dab56c75f"],
            "develop": ["6e30d6236f5d47ebb4be39253eaa6a5dcb487687",
                        "3f4665356a24d76a9461043f62a2b12dab56c75f"]
        }
    }
    results = {
        "3f4665356a24d76a9461043f62a2b12dab56c75f": result1,
        "6e30d6236f5d47ebb4be39253eaa6a5dcb487687": result2,
    }

    # Create mock history manager.
    class History(object):

        def __init__(self, **kwargs):
            super(History, self).__init__(**kwargs)
            self._results = results
            self._history = branch_structure

        def get_result(self, commit):
            return results[commit]

        def iter_branches(self):
            return iteritems(self._history["branches"])

        def build_branch_structure(self):
            pass

        def load_history(self):
            pass

    return History()


def test_structure(mock_history_manager):
    """Expect this one thing to be true."""
    history = mock_history_manager
    results = HistoryReport(history, MOCK_CONFIG).result

    assert set(results.keys()) == set(['cards', 'tests', 'score', 'weights'])
    assert set(results["score"].keys()) == set(['total_score'])
    assert set(
        results["score"]["total_score"].keys()) == \
        set(['history', 'format_type'])
    assert set(results["score"]["total_score"]["history"][0]) == \
        set(["commit", "metric", "branch"])
    assert set(
        results["tests"]["test_parametrized"]["history"]["parameter1"][0]
    ) == set(["commit", "metric", "branch", "data", "result"])
    assert set(results["tests"]["test_number"]["history"][0]) == \
        set(["commit", "metric", "branch", "data", "result"])


def test_score_param(mock_history_manager):
    """Expect all scores to be calculated correctly for parametrized tests."""
    history = mock_history_manager
    score_collection = HistoryReport(
        history, MOCK_CONFIG_SCORES).result['score']
    for score in score_collection["total_score"]["history"]:
        # Equation for result 1:
        # ((((1-0.5)+(1-0.9))/2 + (1-0.2)*1)*1)/(1+1*1)*1
        if score["commit"] == "3f4665356a24d76a9461043f62a2b12dab56c75f":
            assert score["metric"] == 0.55
        # Equation for result 2:
        # ((((1-0)+(1-1))/2 + (1-0.6)*1)*1)/(1+1*1)*1
        if score["commit"] == "6e30d6236f5d47ebb4be39253eaa6a5dcb487687":
            assert score["metric"] == 0.45
