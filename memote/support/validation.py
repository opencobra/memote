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
from cobra.io.sbml3 import (
    parse_stream, get_attrib, read_sbml2,
    parse_xml_into_model, CobraSBMLError)
from tempfile import NamedTemporaryFile
from warnings import catch_warnings, simplefilter


def run_libsbml_validation(path, notifications):
    """Reports errors and warnings from validation with libSBML Python API."""
    validator = SBMLValidator()
    validator.validate(str(path))

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


def run_cobrapy_validation(path, notifications):
    """Reports errors and warnings from validation with cobrapy."""
    with catch_warnings(record=True) as warnings:
        simplefilter("default")
        model = None
        model_ver = None
        try:
            model, model_ver = read_sbml_model(path)
        except Exception as e:
            notifications['errors'].append(str(e))
        notifications['warnings'].extend([str(w.message) for w in warnings])
        return model, model_ver


def read_sbml_model(path, number=float, **kwargs):
    """ Copy of the function cobrapy.io.sbml3.read_sbml_model. """
    xmlfile = parse_stream(path)
    xml = xmlfile.getroot()
    # use libsbml if not l3v1 with fbc v2
    model_ver = (
        xml.get("level"),
        xml.get("version"),
        get_attrib(xml, "fbc:required"))

    use_libsbml = (xml.get("level") != "3" or xml.get("version") != "1" or
                   get_attrib(xml, "fbc:required") is None)

    if use_libsbml:
        if hasattr(path, "read"):
            with NamedTemporaryFile(suffix=".xml", delete=False) as outfile:
                xmlfile.write(outfile, encoding="UTF-8", xml_declaration=True)
            filename = outfile.name
        return read_sbml2(filename, **kwargs), model_ver
    try:
        return parse_xml_into_model(xml, number=number), model_ver
    except Exception:
        raise CobraSBMLError(
            "Something went wrong reading the model. You can get a detailed "
            "report using the `cobra.io.sbml3.validate_sbml_model` function "
            "or using the online validator at http://sbml.org/validator")
