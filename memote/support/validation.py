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

from libsbml import SBMLValidator
from cobra.io.sbml3 import read_sbml_model
from warnings import catch_warnings, simplefilter


def run_libsbml_validation(filename, notifications):
    """Reports errors and warnings from validation with libSBML Python API."""
    validator = SBMLValidator()
    validator.validate(str(filename))

    # Could be relevant later on.
    # doc = validator.getDocument()
    # latest_level = (str(doc.getLevel()) != "3" or str(
    #     doc.getVersion()) != "1" or doc.getPlugin('fbc') == None)

    display_pattern = "Line {}, Column {} - #{}: {} - " \
                      "Category: {}, Severity: {}"
    for i in range(validator.getNumFailures()):
        failure = validator.getFailure(i)
        if failure.isWarning():
            notifications['warnings'].append(display_pattern.format(
                failure.getLine(),
                failure.getColumn(),
                failure.getErrorId(),
                failure.getMessage(),
                failure.getCategoryAsString(),
                failure.getSeverity()))
        else:
            notifications['errors'].append(display_pattern.format(
                failure.getLine(),
                failure.getColumn(),
                failure.getErrorId(),
                failure.getMessage(),
                failure.getCategoryAsString(),
                failure.getSeverity()))


def run_cobrapy_validation(filename, notifications):
    """Reports errors and warnings from validation with cobrapy."""
    with catch_warnings(record=True) as warnings:
        simplefilter("default")
        model = None
        try:
            model = read_sbml_model(filename)
        except Exception as e:
            notifications['errors'].append(str(e))
        notifications['warnings'].extend([str(w.message) for w in warnings])
        return model

