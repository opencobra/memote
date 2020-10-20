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

import pytest


pytest.skip(
    "Thermodynamic tests are disabled until upgrade to new equilibrator-api version.",
    allow_module_level=True,
)


import memote.support.basic as basic  # noqa
import memote.support.thermodynamics as thermo  # noqa
from memote.utils import annotate, get_ids, wrapper  # noqa


@annotate(
    title="Thermodynamic Reversibility of Purely Metabolic Reactions",
    format_type="percent",
)
def test_find_candidate_irreversible_reactions(model):
    u"""
    Identify reversible reactions that could be irreversible.

    If a reaction is neither a transport reaction, a biomass reaction nor a
    boundary reaction, it is counted as a purely metabolic reaction.
    This test checks if the reversibility attribute of each reaction
    agrees with a thermodynamics-based
    calculation of reversibility.

    Implementation:
    To determine reversibility we calculate
    the reversibility index ln_gamma (natural logarithm of gamma) of each
    reaction
    using the eQuilibrator API. We consider reactions, whose reactants'
    concentrations would need to change by more than three orders of
    magnitude for the reaction flux to reverse direction, to be likely
    candidates of irreversible reactions. This assume default concentrations
    around 100 μM (~3 μM—3 mM) at pH = 7, I = 0.1 M and T = 298 K. The
    corresponding reversibility index is approximately 7. For
    further information on the thermodynamic and implementation details
    please refer to
    https://doi.org/10.1093/bioinformatics/bts317 and
    https://pypi.org/project/equilibrator-api/.

    Please note that currently eQuilibrator can only determine the
    reversibility index for chemically and redox balanced reactions whose
    metabolites can be mapped to KEGG compound identifiers (e.g. C00001). In
    addition
    to not being mappable to KEGG or the reaction not being balanced,
    there is a possibility that the metabolite cannot be broken down into
    chemical groups which is essential for the calculation of Gibbs energy
    using group contributions. This test collects each erroneous reaction
    and returns them as a tuple containing each list in the following order:
        1. Reactions with reversibility index
        2. Reactions with incomplete mapping to KEGG
        3. Reactions with metabolites that are problematic during calculation
        4. Chemically or redox unbalanced Reactions (after mapping to KEGG)

    This test simply reports the number of reversible reactions that, according
    to the reversibility index, are likely to be irreversible.

    """
    # With gamma = 1000, ln_gamma ~ 6.9. We use 7 as the cut-off.
    threshold = 7.0
    ann = test_find_candidate_irreversible_reactions.annotation
    met_rxns = basic.find_pure_metabolic_reactions(model)
    (
        rev_index,
        incomplete,
        problematic,
        unbalanced,
    ) = thermo.find_thermodynamic_reversibility_index(met_rxns)
    ann["data"] = (
        # The reversibility index can be infinite so we convert it to a JSON
        # compatible string.
        [(r.id, str(i)) for r, i in rev_index],
        get_ids(incomplete),
        get_ids(problematic),
        get_ids(unbalanced),
    )
    num_irrev = sum(1 for r, i in rev_index if abs(i) >= threshold)
    ann["message"] = wrapper.fill(
        """Out of {} purely metabolic reactions, {} have an absolute
        reversibility index greater or equal to 7 and are therefore likely
        candidates for being irreversible.
        {} reactions could not be mapped to KEGG completely, {} contained
        'problematic' metabolites, and {} are chemically or redox imbalanced.
        """.format(
            len(met_rxns), num_irrev, len(incomplete), len(problematic), len(unbalanced)
        )
    )
    ann["metric"] = num_irrev / len(rev_index)
