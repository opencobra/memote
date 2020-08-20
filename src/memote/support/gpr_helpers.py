# -*- coding: utf-8 -*-

# Copyright 2016 Novo Nordisk Foundation Center for Biosustainability,
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


"""Helper classes and functions for analyzing GPR associations."""


from __future__ import absolute_import

import ast
import logging
import re


__all__ = ("find_top_level_complex",)


logger = logging.getLogger(__name__)
logical_and = re.compile(r"(and)|([&]{1,2})", flags=re.IGNORECASE)
logical_or = re.compile(r"(or)|([|]{1,2})", flags=re.IGNORECASE)
escape_chars = re.compile(r"[.-]")


class DummySet(object):
    """Define a faux set implementation."""

    def add(self, value):
        """Do nothing on adding a value."""
        pass


class GPRVisitor(ast.NodeVisitor):
    """
    Implement a visitor that walks all nodes of an expression tree.

    An abstract syntax tree (AST), generated using ``ast.parse`` on a
    gene-protein-reaction (GPR) association, is traversed and the unique left
    and right elements (genes) of the top level logical AND are recorded.

    Due to using the ``ast`` module, precedence of Boolean operators and general
    syntax requirements follow the Python standard.

    Attributes
    ----------
    left : set
        After walking an AST, this attribute contains unique elements of the
        left branch of the top level binary operator AND. May be empty.
    right : set
        After walking an AST, this attribute contains unique elements of the
        right branch of the top level binary operator AND. May be empty.

    Examples
    --------
    >>> import ast
    >>> expression = ast.parse("g1 or (g2 and g3)")
    >>> walker = GPRVisitor()
    >>> walker.visit(expression)
    >>> walker.left
    {'g2'}
    >>> walker.right
    {'g3'}

    """

    def __init__(self, **kwargs):
        """Initialize a GPR visitor."""
        super(GPRVisitor, self).__init__(**kwargs)
        self.left = set()
        self.right = set()
        self._current = DummySet()
        self._is_top = True

    def generic_visit(self, node):
        logger.debug("%s", type(node).__name__)
        super(GPRVisitor, self).generic_visit(node)

    def visit_BoolOp(self, node):
        """Set up recording of elements with this hook."""
        if self._is_top and isinstance(node.op, ast.And):
            self._is_top = False
            self._current = self.left
            self.visit(node.values[0])
            self._current = self.right
            for successor in node.values[1:]:
                self.visit(successor)
        else:
            self.generic_visit(node)

    def visit_Name(self, node):
        """Record node names on the current branch."""
        self._current.add(node.id)


def find_top_level_complex(gpr):
    """
    Find unique elements of both branches of the top level logical AND.

    Parameters
    ----------
    gpr : str
        The gene-protein-reaction association as a string.

    Returns
    -------
    int
        The size of the symmetric difference between the set of elements to
        the left of the top level logical AND and the right set.

    """
    logger.debug("%r", gpr)
    conform = logical_and.sub("and", gpr)
    conform = logical_or.sub("or", conform)
    conform = escape_chars.sub("_", conform)
    expression = ast.parse(conform)
    walker = GPRVisitor()
    walker.visit(expression)
    return len(walker.left ^ walker.right)
