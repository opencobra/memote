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

from numpydoc.docscrape import NumpyDocString

__all__ = ("register_with", "annotate")


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


def annotate(title, type, message=None, data=None, metric=1.0):
    """Annotate a test case."""
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
