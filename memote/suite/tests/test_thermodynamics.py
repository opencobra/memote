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

"""Perform tests using eQuilibrator API on an instance of ``cobra.Model``."""

from __future__ import absolute_import, division

from sys import version_info

import pytest

if version_info[:2] < (3, 5):
    pytest.skip("Thermodynamic tests require at least Python version 3.5.",
                allow_module_level=True)

import memote.support.thermodynamics as thermo # noqa
import memote.support.basic as basic # noqa
from memote.utils import (annotate, get_ids, truncate) # noqa


@annotate(title="Thermodynamic Reversibility of Purely Metabolic Reactions",
          format_type="percent")
def test_find_incorrect_thermodynamic_reversibility(read_only_model):
    u"""
    Expect reversibility of metabolic reactions to agree with thermodynamics.

    If a reaction is neither a transport reaction, a biomass reaction nor a
    boundary reaction, it is counted as a purely metabolic reaction.
    This test checks if the reversibility attribute of each reaction
    in a list of cobrapy reactions agrees with a thermodynamics-based
    calculation of reversibility. To determine reversibility we calculate
    the reversibility index ln_gamma of each reaction
    using the eQuilibrator API. The default cutoff for ln_gamma of 3
    "corresponds to allowing concentrations to span three orders of magnitude
    around 100 μM (~3 μM—3 mM)" at "pH = 7, I = 0.1 M and T = 298 K". This
    means that a reaction is considered irreversible if the concentration of
    an individual metabolite would have to change more than three orders of
    magnitude i.e. from 3 µM to 3 mM to reverse the direction of flux. For
    further information on the thermodynamic and implementational details
    please refer to
    https://doi.org/10.1093/bioinformatics/bts317 and
    https://gitlab.com/elad.noor/equilibrator-api/tree/master.

    Please note that currently eQuilibrator can only determine the
    reversibility index for chemically and redox balanced reactions whose
    metabolites can be mapped to KEGG compound IDs (e.g. C00001). In addition
    to not being mappable to KEGG or the reaction not being balanced,
    there is a possibility that the metabolite cannot be broken down into
    chemical groups which is essential for the calculation of Gibbs energy
    using component contributions. This test collects each exceptional reaction
    and returns them as a tuple containing each list in the following order:
        1. Reactions with incorrect **rev**ersibility
        2. Reactions with incomplete **mapping** to KEGG
        3. Reactions with Metabolites that are problematic
           during **calc**ulation
        4. Chemically or redox un**bal**anced Reactions (after mapping to KEGG)

    This test simply reports the number of metabolic reactions that disagree
    with thermodynamic calculations i.e. are irreversible even though they
    should not be (and vice versa), considering the above fluctuations of
    metabolite concentrations. It does not have a mandatory 'pass' criterium.

    """
    ann = test_find_incorrect_thermodynamic_reversibility.annotation
    met_rxns = basic.find_pure_metabolic_reactions(read_only_model)
    rev, mapping, calc, bal = \
        thermo.find_incorrect_thermodynamic_reversibility(met_rxns)
    ann["data"] = (get_ids(rev), get_ids(mapping), get_ids(calc), get_ids(bal))
    ann["message"] = "Out of {} purely metabolic reactions the reversibility "\
                     "of {} does not agree with the calculated ln_gamma " \
                     "cutoff ({:.2%}), and thus ought to be inverted. " \
                     "{} reactions " \
                     "could not be mapped to KEGG completely, " \
                     "{} contained 'problematic' metabolites, and " \
                     "{} are chemically or redox imbalanced: {}" \
                     "".format(len(met_rxns), len(ann["data"][0]),
                               ann["metric"], len(ann["data"][1]),
                               len(ann["data"][2]), len(ann["data"][3]),
                               truncate(ann["data"][0]))
    ann["metric"] = (len(ann["data"][0]) +
                     len(ann["data"][1]) +
                     len(ann["data"][2]) +
                     len(ann["data"][3])) / len(met_rxns)
