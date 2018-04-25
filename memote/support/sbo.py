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

"""Supporting functions for sbo checks performed on the model object."""

from __future__ import absolute_import

import logging

LOGGER = logging.getLogger(__name__)


def find_components_without_sbo_terms(model, components):
    """
    Find model components that are not annotated with any SBO terms.

    Parameters
    ----------
    model : cobra.Model
        A cobrapy metabolic model.
    components : {"metabolites", "reactions", "genes"}
        A string denoting `cobra.Model` components.

    Returns
    -------
    list
        The components without any SBO term annotation.

    """
    return [elem for elem in getattr(model, components) if
            elem.annotation is None or 'SBO' not in elem.annotation]


def check_component_for_specific_sbo_term(items, term):
    r"""
    Identify model components that lack a specific SBO term(s).

    Parameters
    ----------
    items : list
        A list of model components i.e. reactions to be checked for a specific
        SBO term.
    term : str or list of str
        A string denoting a valid SBO term matching the regex '^SBO:\d{7}$'
        or a list containing such string elements.

    Returns
    -------
    list
        The components without any or that specific SBO term annotation.

    """
    return [elem for elem in items if
            elem.annotation is None or
            'SBO' not in elem.annotation or
            elem.annotation['SBO'] not in term]
