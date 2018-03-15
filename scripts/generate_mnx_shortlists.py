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

# MetaNetX has been published as:
# MetaNetX/MNXref - reconciliation of metabolites and biochemical reactions to
# bring together genome-scale metabolic networks
# Sébastien Moretti, Olivier Martin, T. Van Du Tran, Alan Bridge,
# Anne Morgat and Marco Pagni
# Nucleic Acids Research (2016), 44(D1):D523-D526
# https://doi.org/10.1093/bioinformatics/btt036
# https://www.metanetx.org/
#

"""Scripts to generate a reduced shortlist from MetaNetX database dumps."""

import pandas as pd

# Read the database dumps in the correct format: remove comment lines, and
# provide appropriate column names.

df = pd.read_csv(
    "chem_xref.tsv",
    delim_whitespace=True,
    comment='#',
    names=['XREF', 'MNX_ID', 'Evidence', 'Description'])


def xref_splitter(xref):
    """
    Return database name from a combined string like "bigg" in "bigg:pyr".

    Return 'mnx' as the ID when the string in xref contains 'MNX' but does not
    contain a colon.

    Parameters
    ----------
    xref : pandas.Dataframe
        The metabolic model under investigation.

    """
    if ':' in xref:
        return xref.split(':')[0]
    elif 'MNX' in xref and ':' not in xref:
        return 'mnx'


# This is the current shortlist, expand this and rerun the script when adding
# new code that requires the identification of key metabolites.
# Included in the list below are energy metabolites, redox cofactors,
# essential amino acids and some vitamins.
shortlist = ['MNXM3', 'MNXM7', 'MNXM51', 'MNXM30', 'MNXM63', 'MNXM220',
             'MNXM121', 'MNXM17', 'MNXM423', 'MNXM495', 'MNXM2', 'MNXM9',
             'MNXM1', 'MNXM10', 'MNXM8', 'MNXM5', 'MNXM6', 'MNXM21',
             'MNXM26', 'MNXM15', 'MNXM89557', 'MNXM38', 'MNXM33',
             'MNXM208',
             'MNXM119', 'MNXM191', 'MNXM232', 'MNXM223', 'MNXM509',
             'MNXM7517',
             'MNXM12235', 'MNXM12233', 'MNXM12236', 'MNXM558', 'MNXM2178',
             'MNXM94', 'MNXM55', 'MNXM134', 'MNXM76', 'MNXM61', 'MNXM97',
             'MNXM53', 'MNXM114', 'MNXM42', 'MNXM142', 'MNXM37', 'MNXM231',
             'MNXM70', 'MNXM78', 'MNXM199', 'MNXM140', 'MNXM32', 'MNXM29',
             'MNXM147', 'MNXM286', 'MNXM360', 'MNXM394', 'MNXM344',
             'MNXM16',
             'MNXM161', 'MNXM12', 'MNXM256',
             'MNXM4']

# Transpose and reshape the dataframe so that we can apply the shortlist
# before the most intensive steps to reduce execution time.
df = df.T
df.columns = df.loc['MNX_ID']
df = df.reindex(df.index.drop('MNX_ID'))

# Slice the original xref dataframe to only include the shortlist metabolites.
xref = df[shortlist]
xref = xref.T.reset_index()

# In chem_xref.tsv, the xref entries are key value pairs separated by ':'
# Such as: bigg:10fthf
# Split xref strings in MNX dump to obtain database names.
xref['XREF_ID'] = xref['XREF'].apply(xref_splitter)

# Obtain the corresponding database IDs from the combined strings in MNX dump.
# This step includes handling old MNX IDs which are stored as
# deprecated:MNXM9996 and makes them available in the mapping.
xref['XREF'] = xref['XREF'].apply(lambda x: x.split(':')[1] if ':' in x else x)

# Group the data in the xref dataframe so that one MNX ID maps to all
# corresponding cross-references from other databases. Then list all
# identifiers that belong to these databases:
# MNX_ID    XREF_ID
# MNXM0     chebi       [23367, 59999]
#           metacyc     [UNKNOWN]
groups = xref.groupby(['MNX_ID', 'XREF_ID'])
xref = groups.apply(lambda x: list(x['XREF']))

# Make a separate column for every XREF_ID:
# MNX_ID    chebi           metacyc
# MNXM0     [23367, 59999]  [UNKNOWN]
xref = xref.unstack('XREF_ID')

# Transpose the dataframe such that the index are now xref databases and the
# column names are metanetx IDs.
xref = xref.T

# Saving the shortlist to memote/support/data
xref.to_json('../memote/support/data/met_id_shortlist.json')
