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

"""Data file validations."""

from __future__ import absolute_import

import json
from os.path import dirname, join

from six import iteritems
from goodtables import validate

from memote.io.checks import gene_id_check, check_partial


def validate_essentiality(filename, model):
    """
    Validate the correctness of essentiality experiment files.

    Parameters
    ----------
    filename : str or pathlib.Path
        Can be a full relative or absolute path.
    model : cobra.Model
        The metabolic model under investigation.

    """
    with open(join(dirname(__file__), "schemata",
                   "essentiality.json")) as file_h:
        schema = json.load(file_h)
    checks = check_partial(gene_id_check, frozenset(g.id for g in model.genes))
    validate(filename, preset='table', schema=schema, order_fields=True,
             custom_checks=checks)


#def validate_data(model):
#    """
#    Validate the presence and correctness of data files.
#
#    Parameters
#    ----------
#    model : cobra.Model
#        The metabolic model under investigation.
#
#    """
#    with open(join(dirname(__file__), "schemata",
#                   "{}.json".format(self.type))) as file_h:
#        schema = json.load(file_h)
#    checks = {
#        "essentiality": [
#
#        ],
#        "growth": [],
#        "production": [],
#    }[self.type]
#    names = {name_part(f): f for f in self.data_files}
#    for exp, obj in iteritems(self.content["experiments"]):
#        assert exp in names
#        # * check gene IDs or whatever IDs
