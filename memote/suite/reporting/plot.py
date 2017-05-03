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

"""Templates for plotly figures."""

from __future__ import absolute_import

import logging

import plotly.offline as py
import plotly.graph_objs as go
from jinja2 import Markup

LOGGER = logging.getLogger(__name__)
_DEFAULT_ARGS = {
    "output_type": "div",
    "include_plotlyjs": False,
    "show_link": False,
    "link_text": ""
}


def scatter_line_chart(df, y_axis, y_title, x_axis="x",
                       x_title="Timestamp", label=None):
    """Generate a reproducible plotly scatter and line plot."""
    figure = {
        "data": [go.Scatter(x=df[x_axis], y=df[y_axis], name=label)],
        "layout": {}
    }
    return Markup(py.plot(figure, **_DEFAULT_ARGS))
