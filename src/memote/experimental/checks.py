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

"""Custom checks for `goodtables`."""

from __future__ import absolute_import

from functools import partial

from goodtables import check


def check_partial(func, *args, **kwargs):
    """Create a partial to be used by goodtables."""
    new_func = partial(func, *args, **kwargs)
    new_func.check = func.check
    return new_func


@check('gene-not-in-model', type='custom', context='body')
def gene_id_check(genes, errors, columns, row_number):
    """
    Validate gene identifiers against a known set.

    Parameters
    ----------
    genes : set
        The known set of gene identifiers.
    errors :
        Passed by goodtables.
    columns :
        Passed by goodtables.
    row_number :
        Passed by goodtables.

    """
    message = ("Gene '{value}' in column {col} and row {row} does not "
               "appear in the metabolic model.")
    for column in columns:
        if "gene" in column['header'] and column['value'] not in genes:
            message = message.format(
                value=column['value'],
                row=row_number,
                col=column['number'])
            errors.append({
                'code': 'bad-value',
                'message': message,
                'row-number': row_number,
                'column-number': column['number'],
            })


@check('reaction-not-in-model', type='custom', context='body')
def reaction_id_check(reactions, errors, columns, row_number):
    """
    Validate reactions identifiers against a known set.

    Parameters
    ----------
    reactions : set
        The known set of reaction identifiers.
    errors :
        Passed by goodtables.
    columns :
        Passed by goodtables.
    row_number :
        Passed by goodtables.

    """
    message = ("Reaction '{value}' in column {col} and row {row} does not "
               "appear in the metabolic model.")
    for column in columns:
        if "reaction" in column['header'] and column['value'] not in reactions:
            message = message.format(
                value=column['value'],
                row=row_number,
                col=column['number'])
            errors.append({
                'code': 'bad-value',
                'message': message,
                'row-number': row_number,
                'column-number': column['number'],
            })


@check('metabolite-not-in-model', type='custom', context='body')
def metabolite_id_check(metabolites, errors, columns, row_number):
    """
    Validate metabolite identifiers against a known set.

    Parameters
    ----------
    metabolites : set
        The known set of metabolite identifiers.
    errors :
        Passed by goodtables.
    columns :
        Passed by goodtables.
    row_number :
        Passed by goodtables.

    """
    message = ("Metabolite '{value}' in column {col} and row {row} does not "
               "appear in the metabolic model.")
    for column in columns:
        if "metabolite" in column['header'] and \
                column['value'] not in metabolites:
            message = message.format(
                value=column['value'],
                row=row_number,
                col=column['number'])
            errors.append({
                'code': 'bad-value',
                'message': message,
                'row-number': row_number,
                'column-number': column['number'],
            })
