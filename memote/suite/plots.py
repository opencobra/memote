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

"""Create various prepared Vega JSON specs."""

from __future__ import absolute_import

import logging

from jinja2 import Markup
from altair import Chart, X, Y, Axis, LayeredChart

LOGGER = logging.getLogger(__name__)


def scatter_line_chart(df, y_axis, y_title, x_axis="x", x_title="Timestamp"):
    """Generate the Vega spec for a point and line plot."""
    chart = LayeredChart(df)
    chart += Chart().mark_circle().encode(
        x=X(x_axis,
            title=x_title,
            axis=Axis(labelAngle=-45, labelAlign="right")),
        y=Y(y_axis,
            title=y_title)
    )
    if len(df) > 1:
        chart += Chart().mark_line().encode(
            x=x_axis,
            y=y_axis
        )
    return Markup(chart.to_json())

