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

"""Helper functions for stoichiometric consistency checks."""

from __future__ import absolute_import, division

import logging
from collections import defaultdict

import numpy as np
import sympy
from six import iteritems, itervalues
from builtins import zip, dict
from pylru import lrudecorator
from optlang.symbolics import add

from memote.support.helpers import find_biomass_reaction

__all__ = (
    "stoichiometry_matrix",
    "nullspace"
)

LOGGER = logging.getLogger(__name__)


def add_reaction_constraints(model, reactions, Constraint):
    """
    Add the stoichiometric coefficients as constraints.

    Parameters
    ----------
    model : optlang.Model
        The transposed stoichiometric matrix representation.
    reactions : iterable
        Container of `cobra.Reaction` instances.
    Constraint : optlang.Constraint
        The constraint class for the specific interface.

    """
    constraints = []
    for rxn in reactions:
        expression = add(
            [c * model.variables[m.id] for m, c in rxn.metabolites.items()])
        constraints.append(Constraint(expression, lb=0, ub=0, name=rxn.id))
    model.add(constraints)


def stoichiometry_matrix(metabolites, reactions):
    """
    Return the stoichiometry matrix representation of a set of reactions.

    The reactions and metabolites order is respected. All metabolites are
    expected to be contained and complete in terms of the reactions.

    Parameters
    ----------
    reactions : iterable
        A somehow ordered list of unique reactions.
    metabolites : iterable
        A somehow ordered list of unique metabolites.

    Returns
    -------
    numpy.array
        The 2D array that represents the stoichiometry matrix.
    dict
        A dictionary mapping metabolites to row indexes.
    dict
        A dictionary mapping reactions to column indexes.

    """
    matrix = np.zeros((len(metabolites), len(reactions)))
    met_index = dict((met, i) for i, met in enumerate(metabolites))
    rxn_index = dict()
    for i, rxn in enumerate(reactions):
        rxn_index[rxn] = i
        for met, coef in iteritems(rxn.metabolites):
            j = met_index[met]
            matrix[j, i] = coef
    return matrix, met_index, rxn_index


def _build_is_zero(atol):
    return sympy.matrices._iszero if atol is None else lambda x: x < atol


def rank(matrix, atol=None):
    """
    Estimate the rank, i.e., the dimension of the column space, of a matrix.

    Parameters
    ----------
    matrix : ndarray
        The matrix should be at most 2-D.  A 1-D array with length k
        will be treated as a 2-D with shape (1, k)
    atol : float
        The absolute tolerance for a zero singular value.  Singular values
        smaller than ``atol`` are considered to be zero. Default: rely on sympy
        definition of 0 (`sympy.matrices._iszero`).

    """
    return sympy.Matrix(np.atleast_2d(matrix)).rank(_build_is_zero(atol=atol))


def nullspace(matrix, atol=None):  # noqa: D402
    """
    Compute normalized basis for the null space (kernel) of a matrix.

    Parameters
    ----------
    matrix : ndarray
        The matrix should be at most 2-D.  A 1-D array with length k
        will be treated as a 2-D with shape (1, k)
    atol : float
        The absolute tolerance for a zero singular value.  Singular values
        smaller than ``atol`` are considered to be zero. Default: rely on sympy
        definition of 0 (`sympy.matrices._iszero`).

    Returns
    -------
    ndarray
        If ``matrix`` is an array with shape (m, k), then the returned
        nullspace will be an array with shape ``(k, n)``, where n is the
        estimated dimension of the nullspace.

    """
    return np.array(
        sympy.Matrix(np.atleast_2d(matrix))
        .nullspace(iszerofunc=_build_is_zero(atol=atol))
    ).T.astype(float)


@lrudecorator(size=2)
def get_interface(model):
    """
    Return the interface specific classes.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return (
        model.solver.interface.Model,
        model.solver.interface.Constraint,
        model.solver.interface.Variable,
        model.solver.interface.Objective
    )


@lrudecorator(size=2)
def get_internals(model):
    """
    Return non-boundary reactions and their metabolites.

    Boundary reactions are unbalanced by their nature. They are excluded here
    and only the metabolites of the others are considered.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    biomass = set(find_biomass_reaction(model))
    if len(biomass) == 0:
        LOGGER.warning("No biomass reaction detected. Consistency test results "
                       "are unreliable if one exists.")
    return set(model.reactions) - (set(model.boundary) | biomass)


def create_milp_problem(kernel, metabolites, Model, Variable, Constraint,
                        Objective):
    """
    Create the MILP as defined by equation (13) in [1]_.

    Parameters
    ----------
    kernel : numpy.array
        A 2-dimensional array that represents the left nullspace of the
        stoichiometric matrix which is the nullspace of the transpose of the
        stoichiometric matrix.
    metabolites : iterable
        The metabolites in the nullspace. The length of this vector must equal
        the first dimension of the nullspace.
    Model : optlang.Model
        Model class for a specific optlang interface.
    Variable : optlang.Variable
        Variable class for a specific optlang interface.
    Constraint : optlang.Constraint
        Constraint class for a specific optlang interface.
    Objective : optlang.Objective
        Objective class for a specific optlang interface.

    References
    ----------
    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    assert len(metabolites) == kernel.shape[0],\
        "metabolite vector and first nullspace dimension must be equal"
    ns_problem = Model()
    k_vars = list()
    for met in metabolites:
        # The element y[i] of the mass vector.
        y_var = Variable(met.id)
        k_var = Variable("k_{}".format(met.id), type="binary")
        k_vars.append(k_var)
        ns_problem.add([y_var, k_var])
        # These following constraints are equivalent to 0 <= y[i] <= k[i].
        ns_problem.add(Constraint(
            y_var - k_var, ub=0, name="switch_{}".format(met.id)))
        ns_problem.add(Constraint(
            y_var, lb=0, name="switch2_{}".format(met.id)))
    ns_problem.update()
    # add nullspace constraints
    for (j, column) in enumerate(kernel.T):
        expression = sympy.Add(
            *[coef * ns_problem.variables[met.id]
              for (met, coef) in zip(metabolites, column) if coef != 0.0])
        constraint = Constraint(expression, lb=0, ub=0,
                                name="ns_{}".format(j))
        ns_problem.add(constraint)
    # The objective is to minimize the binary indicators k[i], subject to
    # the above inequality constraints.
    ns_problem.objective = Objective(1)
    ns_problem.objective.set_linear_coefficients(
        {k_var: 1. for k_var in k_vars})
    ns_problem.objective.direction = "min"
    return ns_problem, k_vars


def add_cut(problem, indicators, bound, Constraint):
    """
    Add an integer cut to the problem.

    Ensure that the same solution involving these indicator variables cannot be
    found by enforcing their sum to be less than before.

    Parameters
    ----------
    problem : optlang.Model
        Specific optlang interface Model instance.
    indicators : iterable
        Binary indicator `optlang.Variable`s.
    bound : int
        Should be one less than the sum of indicators. Corresponds to P - 1 in
        equation (14) in [1]_.
    Constraint : optlang.Constraint
        Constraint class for a specific optlang interface.

    References
    ----------
    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    cut = Constraint(sympy.Add(*indicators), ub=bound)
    problem.add(cut)
    return cut


def is_mass_balanced(reaction):
    """Confirm that a reaction is mass balanced."""
    balance = defaultdict(int)
    for metabolite, coefficient in iteritems(reaction.metabolites):
        if metabolite.elements is None or len(metabolite.elements) == 0:
            return False
        for element, amount in iteritems(metabolite.elements):
            balance[element] += coefficient * amount
    return all(amount == 0 for amount in itervalues(balance))


def is_charge_balanced(reaction):
    """Confirm that a reaction is charge balanced."""
    charge = 0
    for metabolite, coefficient in iteritems(reaction.metabolites):
        if metabolite.charge is None:
            return False
        charge += coefficient * metabolite.charge
    return charge == 0
