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

    def __init__(
        self,
        model,
        sbml_version=None,
        experimental_config=None,
        exclusive=None,
        skip=None,
        **kwargs
    ):
        """
        Collect and store values during testing.

        Parameters
        ----------
        model : cobra.Model
            The metabolic model under investigation.
        sbml_version: tuple, optional
            A tuple reporting on the level, version, and FBC use of
            the SBML file.
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
        self._sbml_ver = sbml_version
        self._exp_config = experimental_config
        self.results = MemoteResult()
        self.results.add_environment_information(self.results.meta)
        self._xcld = frozenset() if exclusive is None else frozenset(exclusive)
        self._skip = frozenset() if skip is None else frozenset(skip)
        if LOGGER.getEffectiveLevel() <= logging.DEBUG:
            self._model.solver.configuration.verbosity = 3

    def pytest_generate_tests(self, metafunc):
        """Parametrize marked functions at runtime."""
        if metafunc.definition.get_closest_marker("biomass"):
            metafunc.parametrize(
                "reaction_id", [rxn.id for rxn in find_biomass_reaction(self._model)]
            )
            return
        # Parametrize experimental test cases.
        for kind in ["essentiality", "growth"]:
            # Find a corresponding pytest marker on the test case.
            if not metafunc.definition.get_closest_marker(kind):
                continue
            exp = getattr(self._exp_config, kind, None)
            if exp is None:
                metafunc.parametrize("experiment", [])
            else:
                names = sorted(exp)
                metafunc.parametrize(
                    "experiment", argvalues=[(n, exp[n]) for n in names], ids=names
                )
            # We only expect one kind of experimental marker per test case
            # and thus end execution here.
            return

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
            LOGGER.debug(
                "Test case '%s' has no annotation (%s).", item.obj.__name__, item.nodeid
            )

    def pytest_report_teststatus(self, report):
        """
        Log pytest results for each test.

        The categories are passed, failed, error, skipped and marked to fail.

        Parameters
        ----------
        report : TestReport
            A test report object from pytest with test case result.

        """
        if report.when == "teardown":
            return
        item_name = report.location[2]

        # Check for a parametrized test.
        match = self._param.search(item_name)
        if match is not None:
            param = match.group("param")
            item_name = item_name[: match.start()]
            LOGGER.debug("%s with parameter %s %s", item_name, param, report.outcome)
        else:
            LOGGER.debug("%s %s", item_name, report.outcome)

        case = self.results.cases.setdefault(item_name, dict())

        if match is not None:
            case["duration"] = case.setdefault("duration", dict())
            case["duration"][param] = report.duration
            case["result"] = case.setdefault("result", dict())
            case["result"][param] = report.outcome
        else:
            case["duration"] = report.duration
            case["result"] = report.outcome

    @pytest.fixture(scope="function")
    def model(self):
        """Provide each test case with a pristine model."""
        with self._model as model:
            yield model

    @pytest.fixture(scope="session")
    def sbml_version(self):
        """Provide SBML level, version, and FBC use."""
        return self._sbml_ver

    def pytest_configure(self, config):
        """Register custom markers at runtime."""
        config.addinivalue_line("markers", "biomass")
        config.addinivalue_line("markers", "essentiality")
        config.addinivalue_line("markers", "growth")
