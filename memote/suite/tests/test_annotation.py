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

"""Annotation tests performed on an instance of `cobra.Model`."""

from __future__ import absolute_import

import memote.support.annotation as annotation


def test_mets_without_annotation(read_only_model, store):
    """Expect all metabolites to have a non-zero annotation attribute."""
    store["metabolites_without_annotations"] = [
        met.id for met in annotation.find_met_without_annotations(
            read_only_model)]
    assert len(store["metabolites_without_annotations"]) == 0, \
        "The following metabolites lack any form of annotation: " \
        "{}".format(", ".join(store["metabolites_without_annotations"]))


def test_rxns_without_annotation(read_only_model, store):
    """Expect all reactions to have a non-zero annotation attribute."""
    store["reactions_without_annotations"] = [
        rxn.id for rxn in annotation.find_rxn_without_annotations(
            read_only_model)]
    assert len(store["reactions_without_annotations"]) == 0, \
        "The following reactions lack any form of annotation: " \
        "{}".format(", ".join(store["reactions_without_annotations"]))
