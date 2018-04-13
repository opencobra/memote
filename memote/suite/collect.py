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

"""Collect results for reporting model quality."""

from __future__ import absolute_import, division

import logging
import re

import pytest

from memote.suite.results.result import MemoteResult
from memote.support.helpers import find_biomass_reaction

LOGGER = logging.getLogger(__name__)


class ResultCollectionPlugin(object):
    """
    Provide functionality for complex test result collection.

    The plugin exposes the fixture ``store`` which can be used in test
    functions to store values in a dictionary. The dictionary is namespaced to
    the module so within a module the same keys should not be re-used
    (unless intended).

    """

    # Match pytest test case names to decide whether they were parametrized.
    # Seems brittle, can we do better?
    _param = re.compile(r"\[(?P<param>[a-zA-Z0-9_.\-]+)\]$")

    def __init__(self, model, experimental_config=None,
                 exclusive=None, skip=None, **kwargs):
        """
        Collect and store values during testing.

        Parameters
        ----------
        model : cobra.Model
            The metabolic model under investigation.
        experimental_config : memote.ExperimentConfiguration, optional
            A description of experiments.
        exclusive : iterable, optional
            Names of test cases or modules to run and exclude all others. Takes
            precedence over ``skip``.
        skip : iterable, optional
            Names of test cases or modules to skip.

        """
        super(ResultCollectionPlugin, self).__init__(**kwargs)
        self._model = model
        self._exp_config = experimental_config
        self.results = MemoteResult()
        self._xcld = frozenset() if exclusive is None else frozenset(exclusive)
        self._skip = frozenset() if skip is None else frozenset(skip)

    def pytest_namespace(self):
        """Insert model information into the pytest namespace."""
        namespace = dict()
        namespace["memote"] = memote = dict()
        memote["biomass_ids"] = [
            rxn.id for rxn in find_biomass_reaction(self._model)]
        memote["compartment_ids"] = sorted(self._model.compartments)
        try:
            memote["compartment_ids"].remove("c")
        except ValueError:
            LOGGER.error(
                "The model does not contain a compartment ID labeled 'c' for "
                "the cytosol which is an essential compartment. Many syntax "
                "tests depend on this being labeled accordingly.")
        # Add experimental information if there are any.
        if self._exp_config is None:
            memote["experimental"] = dict()
            memote["experimental"]["essentiality"] = list()
        else:
            # Load experimental data.
            self._exp_config.load_data(self._model)
            memote["experimental"] = self._exp_config
        return namespace

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_call(self, item):
        """Either run a test exclusively or skip it."""
        if item.obj.__module__ in self._xcld:
            return
        elif item.obj.__name__ in self._xcld:
            return
        elif len(self._xcld) > 0:
            pytest.skip("Excluded.")
        elif item.obj.__module__ in self._skip:
            pytest.skip("Skipped by module.")
        elif item.obj.__name__ in self._skip:
            pytest.skip("Skipped individually.")

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_teardown(self, item):
        """Collect the annotation from each test case and store it."""
        case = self.results.cases.setdefault(item.obj.__name__, dict())
        if hasattr(item.obj, "annotation"):
            case.update(item.obj.annotation)
        else:
            LOGGER.debug("Test case '%s' has no annotation (%s).",
                         item.obj.__name__, item.nodeid)

    def pytest_report_teststatus(self, report):
        """
        Log pytest results for each test.

        The categories are passed, failed, error, skipped and marked to fail.

        Parameters
        ----------
        report : TestReport
            A test report object from pytest with test case result.

        """
        if report.when != "call":
            return
        item_name = report.location[2]

        # Check for a parametrized test.
        match = self._param.search(item_name)
        if match is not None:
            param = match.group("param")
            item_name = item_name[:match.start()]
            LOGGER.debug(
                "%s with parameter %s %s", item_name, param, report.outcome)
        else:
            LOGGER.debug(
                "%s %s", item_name, report.outcome)

        case = self.results.cases.setdefault(item_name, dict())

        if match is not None:
            case["duration"] = case.setdefault("duration", dict())
            case["duration"][param] = report.duration
            case["result"] = case.setdefault("result", dict())
            case["result"][param] = report.outcome
        else:
            case["duration"] = report.duration
            case["result"] = report.outcome

    @pytest.fixture(scope="session")
    def read_only_model(self):
        """Provide the model for the complete test session."""
        return self._model

    @pytest.fixture(scope="function")
    def model(self, read_only_model):
        """Provide a pristine model for a test unit."""
        return self._model.copy()
