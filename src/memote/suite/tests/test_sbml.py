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

"""Tests the level, version and FBC usage of the loaded SBML file."""

from __future__ import absolute_import

from memote.utils import annotate, wrapper


@annotate(title="SBML Level and Version", format_type="raw")
def test_sbml_level(sbml_version):
    """
    Expect the SBML to be at least level 3 version 2.

    This test reports if the model file is represented in the latest edition
    (level) of the Systems Biology Markup Language (SBML) which is Level 3,
    and at least version 1.

    Implementation:
    The level and version are parsed directly from the SBML document.

    """
    version_tag = "SBML Level {} Version {}".format(sbml_version[0], sbml_version[1])
    ann = test_sbml_level.annotation
    ann["data"] = version_tag
    outcome = sbml_version[:2] >= (3, 1)
    ann["metric"] = 1.0 - float(outcome)
    ann["message"] = wrapper.fill("""The SBML file uses: {}""".format(ann["data"]))
    assert sbml_version[:2] >= (3, 1), ann["message"]


@annotate(title="FBC enabled", format_type="raw")
def test_fbc_presence(sbml_version):
    """
    Expect the FBC plugin to be present.

    The Flux Balance Constraints (FBC) Package extends SBML with structured
    and semantic descriptions for domain-specific model components such as
    flux bounds, multiple linear objective functions, gene-protein-reaction
    associations, metabolite chemical formulas, charge and related annotations
    which are relevant for parameterized GEMs and FBA models. The SBML and
    constraint-based modeling communities collaboratively develop this package
    and update it based on user input.

    Implementation:
    Parse the state of the FBC plugin from the SBML document.

    """
    fbc_present = sbml_version[2] is not None
    ann = test_fbc_presence.annotation
    ann["data"] = fbc_present
    ann["metric"] = 1.0 - float(fbc_present)
    if fbc_present:
        ann["message"] = wrapper.fill("The FBC package *is* used.")
    else:
        ann["message"] = wrapper.fill("The FBC package is *not* used.")
    assert fbc_present, ann["message"]
