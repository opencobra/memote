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

"""Supporting functions for stoichiometric consistency checks."""

import logging
import multiprocessing
from operator import attrgetter

import numpy as np
from cobra import Configuration, Reaction
from cobra.exceptions import Infeasible
from cobra.flux_analysis import flux_variability_analysis
from optlang.interface import INFEASIBLE, OPTIMAL
from optlang.symbolics import Zero

import memote.support.consistency_helpers as con_helpers
import memote.support.helpers as helpers


LOGGER = logging.getLogger(__name__)

# The following dictionary is based on the list of energy metabolites chosen
# as part of the following publication:
# Fritzemeier, C. J., Hartleb, D., Szappanos, B., Papp, B., & Lercher,
# M. J. (2017). Erroneous energy-generating cycles in published genome scale
# metabolic networks: Identification and removal. PLoS Computational
# Biology, 13(4), 1–14. http://doi.org/10.1371/journal.pcbi.1005494
ENERGY_COUPLES = {
    "MNXM3": "MNXM7",
    "MNXM63": "MNXM220",
    "MNXM51": "MNXM30",
    "MNXM121": "MNXM17",
    "MNXM423": "MNXM495",
    "MNXM6": "MNXM5",
    "MNXM10": "MNXM8",
    "MNXM38": "MNXM33",
    "MNXM208": "MNXM119",
    "MNXM191": "MNXM232",
    "MNXM223": "MNXM509",
    "MNXM7517": "MNXM12235",
    "MNXM12233": "MNXM12236",
    "MNXM558": "MNXM2178",
    "MNXM21": "MNXM12",
    "MNXM89557": "MNXM20",
}
TOLERANCE_THRESHOLD = 1e-07

cobra_configuration = Configuration()


def check_stoichiometric_consistency(model):
    """
    Verify the consistency of the model's stoichiometry.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    See [1]_ section 3.1 for a complete description of the algorithm.

    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    problem = model.problem
    # The transpose of the stoichiometric matrix N.T in the paper.
    stoich_trans = problem.Model()
    # We clone the existing configuration in order to apply non-default
    # settings, for example, for solver verbosity or timeout.
    stoich_trans.configuration = problem.Configuration.clone(
        config=model.solver.configuration, problem=stoich_trans
    )
    internal_rxns = con_helpers.get_internals(model)
    metabolites = set(met for rxn in internal_rxns for met in rxn.metabolites)
    LOGGER.info("model '%s' has %d internal reactions", model.id, len(internal_rxns))
    LOGGER.info("model '%s' has %d internal metabolites", model.id, len(metabolites))

    stoich_trans.add([problem.Variable(m.id, lb=1) for m in metabolites])
    stoich_trans.update()
    con_helpers.add_reaction_constraints(
        stoich_trans, internal_rxns, problem.Constraint
    )
    # The objective is to minimize the metabolite mass vector.
    stoich_trans.objective = problem.Objective(Zero, direction="min", sloppy=True)
    stoich_trans.objective.set_linear_coefficients(
        {var: 1.0 for var in stoich_trans.variables}
    )
    status = stoich_trans.optimize()
    if status == OPTIMAL:
        return True
    elif status == INFEASIBLE:
        return False
    else:
        raise RuntimeError(
            "Could not determine stoichiometric consistencty."
            " Solver status is '{}'"
            " (only optimal or infeasible expected).".format(status)
        )


def find_unconserved_metabolites(model):
    """
    Detect unconserved metabolites.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    See [1]_ section 3.2 for a complete description of the algorithm.


    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    problem = model.problem
    stoich_trans = problem.Model()
    # We clone the existing configuration in order to apply non-default
    # settings, for example, for solver verbosity or timeout.
    stoich_trans.configuration = problem.Configuration.clone(
        config=model.solver.configuration, problem=stoich_trans
    )
    internal_rxns = con_helpers.get_internals(model)
    metabolites = set(met for rxn in internal_rxns for met in rxn.metabolites)
    # The binary variables k[i] in the paper.
    k_vars = list()
    for met in metabolites:
        # The element m[i] of the mass vector.
        m_var = problem.Variable(met.id)
        k_var = problem.Variable("k_{}".format(met.id), type="binary")
        k_vars.append(k_var)
        stoich_trans.add([m_var, k_var])
        # This constraint is equivalent to 0 <= k[i] <= m[i].
        stoich_trans.add(
            problem.Constraint(k_var - m_var, ub=0, name="switch_{}".format(met.id))
        )
    stoich_trans.update()
    con_helpers.add_reaction_constraints(
        stoich_trans, internal_rxns, problem.Constraint
    )
    # The objective is to maximize the binary indicators k[i], subject to the
    # above inequality constraints.
    stoich_trans.objective = problem.Objective(Zero, sloppy=True, direction="max")
    stoich_trans.objective.set_linear_coefficients({var: 1.0 for var in k_vars})
    status = stoich_trans.optimize()
    if status == OPTIMAL:
        # TODO: See if that could be a Boolean test `bool(var.primal)`.
        return set(
            [
                model.metabolites.get_by_id(var.name[2:])
                for var in k_vars
                if var.primal < 0.8
            ]
        )
    else:
        raise RuntimeError(
            "Could not compute list of unconserved metabolites."
            " Solver status is '{}' (only optimal expected).".format(status)
        )


def find_inconsistent_min_stoichiometry(model, atol=1e-13, max_mets_computed=10):
    """
    Detect inconsistent minimal net stoichiometries.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    atol : float, optional
        Values below the absolute tolerance are treated as zero. Expected to be
        very small but larger than zero.
    max_mets_computed: int, optional
        To avoid computing for too long, a soft cap is added to the number of
        computed unconserved metabolites (trivial cases are ignored).

    Notes
    -----
    See [1]_ section 3.3 for a complete description of the algorithm.

    References
    ----------
    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    if check_stoichiometric_consistency(model):
        return set()
    Model, Constraint, Variable, Objective = con_helpers.get_interface(model)
    unconserved_mets = find_unconserved_metabolites(model)
    LOGGER.info("model has %d unconserved metabolites", len(unconserved_mets))
    internal_rxns = con_helpers.get_internals(model)
    internal_mets = set(met for rxn in internal_rxns for met in rxn.metabolites)
    get_id = attrgetter("id")
    reactions = sorted(internal_rxns, key=get_id)
    metabolites = sorted(internal_mets, key=get_id)
    stoich, met_index, rxn_index = con_helpers.stoichiometry_matrix(
        metabolites, reactions
    )
    left_ns = con_helpers.nullspace(stoich.T, atol)
    if left_ns.size == 0:
        LOGGER.info("Left nullspace is empty!")
        return {(met,) for met in unconserved_mets}
    (problem, indicators) = con_helpers.create_milp_problem(
        left_ns, metabolites, Model, Variable, Constraint, Objective
    )
    # We clone the existing configuration in order to apply non-default
    # settings, for example, for solver verbosity or timeout.
    problem.configuration = model.problem.Configuration.clone(
        config=model.solver.configuration, problem=problem
    )
    LOGGER.info("Left nullspace has a dimension of %d.", left_ns.shape[1])
    LOGGER.debug("%s", str(problem))
    inc_minimal = set()
    cuts = list()
    n_computed = 0
    for met in unconserved_mets:
        # always add the met as an uncoserved set if there is no left nullspace
        row = met_index[met]
        if (left_ns[row] == 0.0).all():
            LOGGER.debug("%s: singleton minimal unconservable set.", met.id)
            # singleton set!
            inc_minimal.add((met,))
            continue
        if n_computed >= max_mets_computed:
            LOGGER.debug("max number of computed unconserved metabolites reached")
            break
        # expect a positive mass for the unconserved metabolite
        problem.variables[met.id].lb = 1e-3
        status = problem.optimize()
        while status == "optimal":
            LOGGER.debug("%s: status %s", met.id, status)
            LOGGER.debug(
                "sum of all primal values: %f", sum(problem.primal_values.values())
            )
            LOGGER.debug(
                "sum of binary indicators: %f", sum(var.primal for var in indicators)
            )
            solution = [
                model.metabolites.get_by_id(var.name[2:])
                for var in indicators
                if var.primal > 0.2
            ]
            LOGGER.debug("%s: set size %d", met.id, len(solution))
            n_computed += 1
            inc_minimal.add(tuple(solution))
            if len(solution) == 1:
                break
            cuts.append(
                con_helpers.add_cut(problem, indicators, len(solution) - 1, Constraint)
            )
            status = problem.optimize()
        LOGGER.debug("%s: last status %s", met.id, status)
        # reset
        problem.variables[met.id].lb = 0.0
        problem.remove(cuts)
        cuts.clear()
    return inc_minimal


def find_elementary_leakage_modes(model, atol=1e-13):
    """
    Detect elementary leakage modes.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    atol : float, optional
        Values below the absolute tolerance are treated as zero. Expected to be
        very small but larger than zero.

    Notes
    -----
    See [1]_ section 3.4 for a complete description of the algorithm.

    References
    ----------
    .. [1] Gevorgyan, A., M. G Poolman, and D. A Fell.
           "Detection of Stoichiometric Inconsistencies in Biomolecular
           Models."
           Bioinformatics 24, no. 19 (2008): 2245.

    """
    raise NotImplementedError("Coming soon™ if considered useful.")


def detect_energy_generating_cycles(model, metabolite_id):
    u"""
    Detect erroneous energy-generating cycles for a a single metabolite.

    The function will first build a dissipation reaction corresponding to the
    input metabolite. This reaction is then set as the objective for
    optimization, after closing all exchanges. If the reaction was able to
    carry flux, an erroneous energy-generating cycle must be present. In this
    case a list of reactions with a flux greater than zero is returned.
    Otherwise, the function returns False.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    metabolite_id : str
        The identifier of an energy metabolite.

    Notes
    -----
    "[...] energy generating cycles (EGC) [...] charge energy metabolites
    without a source of energy. [...] To efficiently identify the existence of
    diverse EGCs, we first add a dissipation reaction to the metabolic network
    for each metabolite used to transmit cellular energy; e.g., for ATP, the
    irreversible reaction ATP + H2O → ADP + P + H+ is added. These dissipation
    reactions close any existing energy-generating cycles, thereby converting
    them to type-III pathways. Fluxes through any of the dissipation reactions
    at steady state indicate the generation of energy through the metabolic
    network. Second, all uptake reactions are constrained to zero. The sum of
    the fluxes through the energy dissipation reactions is now maximized using
    FBA. For a model without EGCs, these reactions cannot carry any flux
    without the uptake of nutrients. [1]_."

    References
    ----------
    .. [1] Fritzemeier, C. J., Hartleb, D., Szappanos, B., Papp, B., & Lercher,
     M. J. (2017). Erroneous energy-generating cycles in published genome scale
     metabolic networks: Identification and removal. PLoS Computational
     Biology, 13(4), 1–14. http://doi.org/10.1371/journal.pcbi.1005494

    """
    main_comp = helpers.find_compartment_id_in_model(model, "c")
    met = helpers.find_met_in_model(model, metabolite_id, main_comp)[0]

    dissipation_rxn = Reaction("Dissipation")
    if metabolite_id in ["MNXM3", "MNXM63", "MNXM51", "MNXM121", "MNXM423"]:
        # build nucleotide-type dissipation reaction
        dissipation_rxn.add_metabolites(
            {
                helpers.find_met_in_model(model, "MNXM2", main_comp)[0]: -1,
                helpers.find_met_in_model(model, "MNXM1", main_comp)[0]: 1,
                helpers.find_met_in_model(model, "MNXM9", main_comp)[0]: 1,
            }
        )
    elif metabolite_id in ["MNXM6", "MNXM10"]:
        # build nicotinamide-type dissipation reaction
        dissipation_rxn.add_metabolites(
            {helpers.find_met_in_model(model, "MNXM1", main_comp)[0]: 1}
        )
    elif metabolite_id in [
        "MNXM38",
        "MNXM208",
        "MNXM191",
        "MNXM223",
        "MNXM7517",
        "MNXM12233",
        "MNXM558",
    ]:
        # build redox-partner-type dissipation reaction
        dissipation_rxn.add_metabolites(
            {helpers.find_met_in_model(model, "MNXM1", main_comp)[0]: 2}
        )
    elif metabolite_id == "MNXM21":
        dissipation_rxn.add_metabolites(
            {
                helpers.find_met_in_model(model, "MNXM2", main_comp)[0]: -1,
                helpers.find_met_in_model(model, "MNXM1", main_comp)[0]: 1,
                helpers.find_met_in_model(model, "MNXM26", main_comp)[0]: 1,
            }
        )
    elif metabolite_id == "MNXM89557":
        dissipation_rxn.add_metabolites(
            {
                helpers.find_met_in_model(model, "MNXM2", main_comp)[0]: -1,
                helpers.find_met_in_model(model, "MNXM1", main_comp)[0]: 2,
                helpers.find_met_in_model(model, "MNXM15", main_comp)[0]: 1,
            }
        )

    dissipation_product = helpers.find_met_in_model(
        model, ENERGY_COUPLES[metabolite_id], main_comp
    )[0]

    dissipation_rxn.add_metabolites({met: -1, dissipation_product: 1})
    helpers.close_boundaries_sensibly(model)
    model.add_reactions([dissipation_rxn])
    model.objective = dissipation_rxn
    solution = model.optimize(raise_error=True)

    if solution.objective_value > 0.0:
        return (
            solution.fluxes[solution.fluxes.abs() > 0.0]
            .index.drop(["Dissipation"])
            .tolist()
        )
    else:
        return []


def find_mass_unbalanced_reactions(reactions):
    """
    Find metabolic reactions that are not mass balanced.

    Parameters
    ----------
    reactions : iterable
        An iterable of cobra.Reaction's.

    """
    return [rxn for rxn in reactions if not con_helpers.is_mass_balanced(rxn)]


def find_charge_unbalanced_reactions(reactions):
    """
    Find metabolic reactions that are not charge balanced.

    Parameters
    ----------
    reactions : iterable
        An iterable of cobra.Reaction's.

    """
    return [rxn for rxn in reactions if not con_helpers.is_charge_balanced(rxn)]


def find_stoichiometrically_balanced_cycles(model):
    u"""
    Find metabolic reactions in stoichiometrically balanced cycles (SBCs).

    Identify forward and reverse cycles by closing all exchanges and using FVA.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Notes
    -----
    "SBCs are artifacts of metabolic reconstructions due to insufficient
    constraints (e.g., thermodynamic constraints and regulatory
    constraints) [1]_." They are defined by internal reactions that carry
    flux in spite of closed exchange reactions.

    References
    ----------
    .. [1] Thiele, I., & Palsson, B. Ø. (2010, January). A protocol for
           generating a high-quality genome-scale metabolic reconstruction.
           Nature protocols. Nature Publishing Group.
           http://doi.org/10.1038/nprot.2009.203

    """
    helpers.close_boundaries_sensibly(model)
    fva_result = flux_variability_analysis(model, loopless=False)
    return fva_result.index[
        (fva_result["minimum"] <= (-1 + TOLERANCE_THRESHOLD))
        | (fva_result["maximum"] >= (1 - TOLERANCE_THRESHOLD))
    ].tolist()


def find_orphans(model):
    """
    Return metabolites that are only consumed in reactions.

    Metabolites that are involved in an exchange reaction are never
    considered to be orphaned.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    exchanges = frozenset(model.exchanges)
    return [
        met
        for met in model.metabolites
        if (len(met.reactions) > 0)
        and all(
            (rxn not in exchanges) and con_helpers.is_only_substrate(met, rxn)
            for rxn in met.reactions
        )
    ]


def find_deadends(model):
    """
    Return metabolites that are only produced in reactions.

    Metabolites that are involved in an exchange reaction are never
    considered to be dead ends.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    exchanges = frozenset(model.exchanges)
    return [
        met
        for met in model.metabolites
        if (len(met.reactions) > 0)
        and all(
            (rxn not in exchanges) and con_helpers.is_only_product(met, rxn)
            for rxn in met.reactions
        )
    ]


def find_disconnected(model):
    """
    Return metabolites that are not in any of the reactions.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    """
    return [met for met in model.metabolites if len(met.reactions) == 0]


def _init_worker(model, variable_name, coefficient):
    """
    Initialize a global model object for multiprocessing.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    variable_name: str
        The name of the variable representing the metabolite exchange.
    coefficient: int
        The value of the metabolite's stoichiometric coefficient: -1 to test
        if the model can produce the metabolite and 1 to test if it can be
        consumed.

    """
    global _model
    global _sink
    global _coefficient
    _model = model
    _sink = model.variables[variable_name]
    _model.objective = _sink
    _coefficient = coefficient


def _solve_metabolite_exchange(metabolite_id):
    """
    Solve for a metabolite's exchange flux.

    By adding the exchange variable to the metabolite constraint,
    the solution tests whether the metabolic model produce or consume the
    metabolite.

    Notes
    -----
    The model, exchange variable, and stoichiometric coefficient are globals.

    Parameters
    ----------
    metabolite_id: str
        The exchange will be added to this metabolite as a linear coefficient.

    Returns
    -------
    float
        The numeric value of the solution of the flux-balance problem; *NaN* if
        infeasible.
    str
        The identifier of the considered metabolite.

    """
    global _model
    global _sink
    global _coefficient
    constraint = _model.constraints[metabolite_id]
    constraint.set_linear_coefficients({_sink: _coefficient})
    solution = _model.slim_optimize()
    constraint.set_linear_coefficients({_sink: 0})
    return solution, metabolite_id


def find_blocked_metabolites(model, coefficient, processes=None):
    """
    Return metabolite identifiers that cannot be produced or consumed.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    coefficient: int
        Test if production is possible with -1 and consumption with 1.
    processes: int, optional
        Number of processes to be used (the default is taken from
        `cobra.Configuration.processes`).

    Returns
    -------
    list
        The identifiers of blocked metabolites.

    """
    if processes is None:
        processes = cobra_configuration.processes
    met_identifiers = [m.id for m in model.metabolites]
    num_mets = len(met_identifiers)
    processes = min(processes, num_mets)

    with model:
        helpers.open_exchanges(model)
        sink = model.problem.Variable("__multi_sink", lb=0, ub=1000)
        model.add_cons_vars([sink])
        model.solver.update()

        if processes > 1:
            chunk_size = num_mets // processes
            pool = multiprocessing.Pool(
                processes,
                initializer=_init_worker,
                initargs=(model, sink.name, coefficient),
            )
            result_iter = pool.imap_unordered(
                _solve_metabolite_exchange, met_identifiers, chunksize=chunk_size
            )
            pool.close()
            blocked = [
                met_id
                for solution, met_id in result_iter
                if np.isnan(solution) or solution < model.tolerance
            ]
            pool.join()
        else:
            _init_worker(model, sink.name, coefficient)
            blocked = [
                met_id
                for solution, met_id in map(_solve_metabolite_exchange, met_identifiers)
                if np.isnan(solution) or solution < model.tolerance
            ]
    return sorted(blocked)


def find_metabolites_not_produced_with_open_bounds(model, processes=None):
    """
    Return metabolite identifiers that cannot be produced with open exchanges.

    A perfect model should be able to produce each and every metabolite when
    all medium components are available.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    processes: int, optional
        Number of processes to be used (the default is taken from
        `cobra.Configuration.processes`).

    Returns
    -------
    list
        The metabolite identifiers that could not be produced.

    """
    return find_blocked_metabolites(model, -1, processes=processes)


def find_metabolites_not_consumed_with_open_bounds(model, processes=None):
    """
    Return metabolite identifiers that cannot be consumed with open exchanges.

    When all metabolites can be secreted, it should be possible for each and
    every metabolite to be consumed in some form.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.
    processes: int, optional
        Number of processes to be used (the default is taken from
        `cobra.Configuration.processes`).

    Returns
    -------
    list
        The metabolite identifiers that could not be consumed.

    """
    return find_blocked_metabolites(model, 1, processes=processes)


def find_reactions_with_unbounded_flux_default_condition(model):
    """
    Return list of reactions whose flux is unbounded in the default condition.

    Parameters
    ----------
    model : cobra.Model
        The metabolic model under investigation.

    Returns
    -------
    tuple
        list
            A list of reactions that in default modeling conditions are able to
            carry flux as high/low as the systems maximal and minimal bounds.
        float
            The fraction of the amount of unbounded reactions to the amount of
            non-blocked reactions.
        list
            A list of reactions that in default modeling conditions are not able
            to carry flux at all.

    """
    try:
        fva_result = flux_variability_analysis(model, fraction_of_optimum=1.0)
    except Infeasible as err:
        LOGGER.error(
            "Failed to find reactions with unbounded flux "
            "because '{}'. This may be a bug.".format(err)
        )
        raise Infeasible(
            "It was not possible to run flux variability "
            "analysis on the model. Make sure that the model "
            "can be solved! Check if the constraints are not "
            "too strict."
        )
    # Per reaction (row) the flux is below threshold (close to zero).
    conditionally_blocked = fva_result.loc[
        fva_result.abs().max(axis=1) < TOLERANCE_THRESHOLD
    ].index.tolist()
    small, large = helpers.find_bounds(model)
    # Find those reactions whose flux is close to or outside of the median
    # upper or lower bound, i.e., appears unconstrained.
    unlimited_flux = fva_result.loc[
        np.isclose(fva_result["maximum"], large, atol=TOLERANCE_THRESHOLD)
        | (fva_result["maximum"] > large)
        | np.isclose(fva_result["minimum"], small, atol=TOLERANCE_THRESHOLD)
        | (fva_result["minimum"] < small)
    ].index.tolist()
    try:
        fraction = len(unlimited_flux) / (
            len(model.reactions) - len(conditionally_blocked)
        )
    except ZeroDivisionError:
        LOGGER.error(
            "Division by Zero! Failed to calculate the "
            "fraction of unbounded reactions. Does this model "
            "have any reactions at all?"
        )
        raise ZeroDivisionError(
            "It was not possible to calculate the "
            "fraction of unbounded reactions to "
            "un-blocked reactions. This may be because"
            "the model doesn't have any reactions at "
            "all or that none of the reactions can "
            "carry a flux larger than zero!"
        )

    return unlimited_flux, fraction, conditionally_blocked
