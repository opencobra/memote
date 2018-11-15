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

"""Supporting functions for checks requiring the eQuilibrator-API."""

from __future__ import absolute_import

from equilibrator_api import ComponentContribution, Reaction, ReactionMatcher
from six import string_types
from memote.support import helpers

def smallest_compound_ID(kegg_ann_list):
    """
    Return an ascending list filtered to contain only KEGG compound IDs.

    KEGG IDs may map to compounds, drugs and glycans prefixed respectively
    with "C", "D", and "G" followed by at least 5 digits.

    Parameters
    ----------
    kegg_ann_list: list
        A list of mixed KEGG IDs.

    """
    only_cIDs = [x for x in kegg_ann_list if "C" in x]
    only_cIDs.sort(key=lambda x: int(x.lstrip('C')))
    return only_cIDs[0]

def get_equilibrator_rxn_string(rxn):
    """
    Return a reaction string with at least a partial mapping to KEGG IDs.

    First see if there is an unambiguous mapping to a single KEGG compound ID
    provided with the model. If not, check if there is any KEGG compound ID in
    a list of mappings. KEGG IDs may map to compounds, drugs and glycans. KEGG
    compound IDs are sorted so we keep the lowest that is there. If none of
    this works try mapping to KEGG via the CompoundMatcher by the name of the
    metabolite. If the metabolite cannot be mapped we simply don't replace it
    in the original reaction string.

    Parameters
    ----------
    rxn: cobra.Reaction
        The metabolic reaction under investigation.

    """
    kegg_rxn = rxn.reaction
    for met in rxn.metabolites:
        kegg_ann_id = met.annotation.get("kegg.compound")
        if isinstance(kegg_ann_id, string_types) and "C" in kegg_ann_id:
            kegg_rxn = kegg_rxn.replace(met.id, kegg_ann_id)
        elif type(kegg_ann_id) is list and any("C" in s for s in kegg_ann_id):
            kegg_rxn = kegg_rxn.replace(
                met.id, smallest_compound_ID(kegg_ann_id)
            )
        else:
            try:
                df = cm.match(met.name)
                kegg_match_id = df['CID'].iloc[0]
                kegg_rxn = kegg_rxn.replace(met.id, kegg_match_id)
            except:
                pass
    # COBRApy reaction strings seem to use slightly different arrows which
    # are not recognized by the eQuilibrator-API
    return kegg_rxn.replace('-->', '->').replace('<--', '<-')