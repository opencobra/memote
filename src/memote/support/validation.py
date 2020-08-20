# -*- coding: utf-8 -*-

# Copyright 2019 Novo Nordisk Foundation Center for Biosustainability,
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


"""Structurally validate SBML-formatted file input."""


from __future__ import absolute_import

from warnings import catch_warnings, simplefilter

import libsbml
from cobra.io import read_sbml_model


def load_cobra_model(path, notifications):
    """Load a COBRA model with meta information from an SBML document."""
    doc = libsbml.readSBML(path)
    fbc = doc.getPlugin("fbc")
    sbml_ver = (
        doc.getLevel(),
        doc.getVersion(),
        fbc if fbc is None else fbc.getVersion(),
    )
    with catch_warnings(record=True) as warnings:
        simplefilter("always")
        try:
            model = read_sbml_model(path)
        except Exception as err:
            notifications["errors"].append(str(err))
            model = None
            validate = True
        else:
            validate = False
        notifications["warnings"].extend([str(w.message) for w in warnings])
    if validate:
        run_sbml_validation(doc, notifications)
    return model, sbml_ver


def format_failure(failure):
    """Format how an error or warning should be displayed."""
    return "Line {}, Column {} - #{}: {} - Category: {}, Severity: {}".format(
        failure.getLine(),
        failure.getColumn(),
        failure.getErrorId(),
        failure.getMessage(),
        failure.getCategoryAsString(),
        failure.getSeverity(),
    )


def run_sbml_validation(document, notifications):
    """Report errors and warnings found in an SBML document."""
    validator = libsbml.SBMLValidator()
    validator.validate(document)
    for i in range(document.getNumErrors()):
        notifications["errors"].append(format_failure(document.getError(i)))
    for i in range(validator.getNumFailures()):
        failure = validator.getFailure(i)
        if failure.isWarning():
            notifications["warnings"].append(format_failure(failure))
        else:
            notifications["errors"].append(format_failure(failure))
