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


"""
(me)tabolic (mo)del (te)sts.

The memote Python package is a community-driven effort towards a standardized
genome-scale metabolic model test suite.
"""


__author__ = "Moritz E. Beber"
__email__ = "midnighter@posteo.net"


from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions


from memote.utils import show_versions
from memote.suite.api import *
from memote.suite.results import *
from memote.suite.reporting import *
from memote.jinja2_extension import *
