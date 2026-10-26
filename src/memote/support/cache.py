# -*- coding: utf-8 -*-

# Copyright 2026 Zijian Zeng.
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

"""Explicit lifecycle for model-dependent support caches."""

from memote.support import basic, consistency_helpers, helpers


def clear_support_caches():
    """Clear cached support results for all model instances.

    Call after mutating a model before reusing support functions directly.
    ``test_model`` calls this once at entry, preserving reuse within each run.
    This global reset does not track within-run mutations or synchronize
    concurrent calls. Entries may remain after a run until reset or eviction.
    """
    for function in (
        helpers.find_transport_reactions,
        helpers.find_biomass_reaction,
        helpers.find_demand_reactions,
        helpers.find_sink_reactions,
        helpers.find_exchange_rxns,
        helpers.find_bounds,
        consistency_helpers.get_interface,
        consistency_helpers.get_internals,
        basic.find_pure_metabolic_reactions,
        basic.find_duplicate_metabolites_in_compartments,
    ):
        function.clear()
