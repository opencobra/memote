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

"""Configuration and fixtures for the py.test suite."""

from __future__ import absolute_import

from os.path import join, dirname

import pytest
from cobra.io import read_sbml_model
from optlang import available_solvers
from cobra import Model

pytest_plugins = ["pytester"]

# Gurobi MILP is currently not fully supported in optlang.
# A MOSEK interface still needs to be completed.
SUPPORTED_SOLVERS = [solver for solver in ["glpk", "cplex"]
                     if available_solvers[solver.upper()]]


@pytest.fixture(scope="session", params=SUPPORTED_SOLVERS)
def solver(request):
    return request.param


@pytest.fixture(scope="session", params=["ecoli-core"])
def small_file(request):
    if request.param == "ecoli-core":
        return join(dirname(__file__), "data", "EcoliCore.xml.gz")


@pytest.fixture(scope="function")
def model(request, solver):
    if request.param == "empty":
        model = Model(id_or_model=request.param, name=request.param)
    elif request.param == "textbook":
        model = read_sbml_model(join(dirname(__file__), "data",
                                     "EcoliCore.xml.gz"))
    else:
        builder = getattr(request.module, "MODEL_REGISTRY")[request.param]
        model = builder(Model(id_or_model=request.param, name=request.param))
    model.solver = solver
    return model


@pytest.fixture(scope="session",
                params=["e", "pp", "c"])
def compartment_suffix(request):
    return request.param
