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

from builtins import dict
from textwrap import TextWrapper

__all__ = ("register_with", "annotate", "get_ids", "truncate")


LIST_SLICE = 5
FLOAT_FORMAT = 7.2

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
def annotate(title, type, message=None, data=None, metric=1.0):
    """
    Annotate a test case.

    Parameters
    ----------
    title : str
        A human-readable descriptive title of the test case.
    type : str
        A sting that determines how the result data is formatted in the report.
        - 'array' : The tested quality is represented as a list, e.g. all
          biomass reactions in the model. In the angular report, 'data' is
          interpreted as a list. It is expected not to be None.
        - 'length' : The tested quality is represented as the
          length of a list, set or tuple, e.g. number of metabolites without
          formula. In the angular report, 'data' is interpreted as a list. It
          is expected not to be None.
        - 'number' : The tested quality is represented as a percentage, e.g.
          percentage of metabolites without charge. In the angular report,
          'metric' is used and expected to be a floating point number.
        - 'object' : Use only if the test case is parametrized i.e. if the
          same basic test logic can be applied to several tested components,
          such as testing for the presence of annotations for specific
          databases for all metabolites. In the angular report, 'data' is
          interpreted as a dictionary whose values can be dictionaries, lists,
          strings, floats and integers. It is expected not to be None.
        - 'string' : The tested quality is represented as a single string,
          e.g. the ID of the model. In the angular report, 'data' is
          interpreted as a string. It is expected not to be None.
    message : str
        A short written explanation that states and possibly explains the test
        result.
    data
        Raw data which the test case generates and assesses. Can be of the
        following types: list, set, tuple, string, float, integer, boolean and
        dictionary.
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
    types = ['array', 'length', 'number', 'object', 'string']
    if type not in types:
        raise ValueError("Invalid type. Expected one of: %s" % types)

    def decorator(func):
        func.annotation = dict(
            title=title,
            summary=func.__doc__,
            message=message,
            data=data,
            type=type,
            metric=metric)
        return func
    return decorator


def get_ids(iterable):
    """Retrieve the identifier of a number of objects."""
    return [element.id for element in iterable]


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
