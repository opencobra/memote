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


def scatter_line_chart(df, y_title):
    """Generate a reproducible plotly scatter and line plot."""
    if len(df.columns) == 3:
        x_axis, y_axis, factor = df.columns
        data = go.Data([
            go.Scatter(x=sub[x_axis], y=sub[y_axis], name=key)
            for key, sub in df.groupby(factor, as_index=False, sort=False)])
    else:
        x_axis, y_axis = df.columns
        data = go.Data([
            go.Scatter(x=df[x_axis], y=df[y_axis])])
    layout = go.Layout(
        width=650,
        height=500,
        xaxis=go.XAxis(
            title="Commit Hash" if x_axis == "commit_hash" else "Timestamp",
            tickangle=-45 if x_axis == "commit_hash" else 0
        ),
        yaxis=go.YAxis(
            title=y_title
        )
    )
    return Markup(py.plot(go.Figure(data=data, layout=layout), **_DEFAULT_ARGS))


def boolean_chart(df, y_title):
    """Generate a reproducible plotly scatter and line plot."""
    if len(df.columns) == 3:
        x_axis, y_axis, factor = df.columns
        data = go.Data([
            go.Scatter(x=sub[x_axis], y=sub[y_axis].astype(int), name=key)
            for key, sub in df.groupby(factor, as_index=False, sort=False)])
    else:
        x_axis, y_axis = df.columns
        data = go.Data([
            go.Scatter(x=df[x_axis], y=df[y_axis].astype(int))])
    layout = go.Layout(
        width=650,
        height=500,
        xaxis=go.XAxis(
            title="Commit Hash" if x_axis == "commit_hash" else "Timestamp",
            tickangle=-45 if x_axis == "commit_hash" else 0
        ),
        yaxis=go.YAxis(
            title=y_title,
            zeroline=False,
            tickmode="array",
            tickvals=[0, 1],
            ticktext=["No", "Yes"]
        )
    )
    return Markup(py.plot(go.Figure(data=data, layout=layout), **_DEFAULT_ARGS))
