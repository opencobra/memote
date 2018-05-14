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

"""Utility functions used by memote and its tests."""

from __future__ import absolute_import

import logging
from builtins import dict, str
from numpydoc.docscrape import NumpyDocString
from textwrap import TextWrapper
from depinfo import print_dependencies

__all__ = ("register_with", "annotate", "get_ids",
           "get_ids_and_bounds", "truncate", "wrapper",
           "log_json_incompatible_types", "show_versions")

LOGGER = logging.getLogger(__name__)

LIST_SLICE = 5
FLOAT_FORMAT = 7.2
TYPES = frozenset(['count', 'number', 'raw', 'percent'])
JSON_TYPES = (type(None), bool, int, float, str, list, dict)

wrapper = TextWrapper(width=70)


def register_with(registry):
    """
    Register a passed in object.

    Intended to be used as a decorator on model building functions with a
    ``dict`` as a registry.

    Examples
    --------
    REGISTRY = dict()
    @register_with(REGISTRY)
    def build_empty(base):
        return base

    """
    def decorator(func):
        registry[func.__name__] = func
        return func
    return decorator


# TODO: Change naming of the 'type' argument once the angular app is completed.
# It is misleading.
def annotate(title, format_type, message=None, data=None, metric=1.0):
    """
    Annotate a test case.

    Parameters
    ----------
    title : str
        A human-readable descriptive title of the test case.
    format_type : str
        A string that determines how the result data is formatted in the
        report. It is expected not to be None.
        - 'number' : 'data' is a single number which can be an integer or
          float and should be represented as such.
        - 'count' : 'data' is a list, set or tuple. Choosing 'count' will
          display the length of that list e.g. number of metabolites without
          formula.
        - 'percent' : Instead of 'data' the content of 'metric' ought to be
          displayed e.g. percentage of metabolites without charge.
          'metric' is expected to be a floating point number.
        - 'raw' : 'data' is ought to be displayed "as is" without formatting.
          This option is appropriate for single strings or a boolean output.
    message : str
        A short written explanation that states and possibly explains the test
        result.
    data
        Raw data which the test case generates and assesses. Can be of the
        following types: list, set, tuple, string, float, integer, and boolean.
    metric: float
        A value x in the range of 0 <= x <= 1 which represents the fraction of
        'data' to the total in the model. For example, if 'data' are all
        metabolites without formula, 'metric' should be the fraction of
        metabolites without formula from the total of metabolites in the model.

    Returns
    -------
    function
        The decorated function, now extended by the attribute 'annotation'.

    Notes
    -----
    Adds "annotation" attribute to the function object, which stores values for
    predefined keys as a dictionary.

    """
    if format_type not in TYPES:
        raise ValueError(
            "Invalid type. Expected one of: {}.".format(", ".join(TYPES)))

    def decorator(func):
        func.annotation = dict(
            title=title,
            summary=extended_summary(func),
            message=message,
            data=data,
            format_type=format_type,
            metric=metric)
        return func
    return decorator


def get_ids(iterable):
    """Retrieve the identifier of a number of objects."""
    return [element.id for element in iterable]


def get_ids_and_bounds(iterable):
    """Retrieve the identifier and bounds of a  number of objects."""
    return ["{0.lower_bound} <= {0.id} <= {0.upper_bound}".format(elem) for
            elem in iterable]


def truncate(sequence):
    """
    Create a potentially shortened text display of a list.

    Parameters
    ----------
    sequence : list
        An indexable sequence of elements.

    Returns
    -------
    str
        The list as a formatted string.

    """
    if len(sequence) > LIST_SLICE:
        return ", ".join(sequence[:LIST_SLICE] + ["..."])
    else:
        return ", ".join(sequence)


def log_json_incompatible_types(obj):
    """
    Log types that are not JSON compatible.

    Explore a nested dictionary structure and log types that are not JSON
    compatible.

    Parameters
    ----------
    obj : dict
        A potentially nested dictionary.

    """
    keys_to_explore = list(obj)
    while len(keys_to_explore) > 0:
        key = keys_to_explore.pop()
        if not isinstance(key, str):
            LOGGER.debug(type(key))
        value = obj[key]
        if isinstance(value, dict):
            LOGGER.debug("%s:", key)
            log_json_incompatible_types(value)
        elif not isinstance(value, JSON_TYPES):
            LOGGER.debug("%s: %s", key, type(value))


def extended_summary(func):
    """
    Show the extended summary of a function's docstring.

    Parameters
    ----------
    func : function
        A scored or unscored test function used in `memote report snapshot`

    Returns
    -------
    str
        The extended summary of the docstring of func

    """
    doc = NumpyDocString(func.__doc__)
    return "\n".join(doc["Extended Summary"])


def show_versions():
    """Print formatted dependency information to stdout."""
    print_dependencies("memote")
