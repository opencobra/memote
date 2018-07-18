.. highlight:: shell

=================
Experimental Data
=================

.. contents:: Sections
   :depth: 2
   :local:

At the moment it is possible to include the following types of experimental data
with your model tests.

1. Growth data, for example, processed Biolog data, that lists whether growth
   was possible in different media.
2. Gene essentiality data that lists for a single gene identifier whether it is
   essential, i.e., a knock-out is lethal, or not.

In order for memote to make proper use of your data, you should add them to the
repository. If you use ``memote new`` to generate the repository structure, take
a look at the files under ``data``. It should look like this:

.. code-block:: console

    data
    ├── essentiality
    ├── experiments.yml
    ├── growth
    └── media

Configuration
=============

In order for anything to happen you have to edit the ``experiments.yml``
configuration file. The provided file contains a minimal setup but does not
actually define any experiments.

.. code-block:: yaml

    version: "0.1"
    medium:
      path: "media/"
    essentiality:
      path: "essentiality/"
    growth:
      path: "growth/"

The file simply states that files relating to media, essentiality, and growth
experiments can be found at directories stated under ``path:`` relative to the
location of the file.

Media
=====

You can fill the configuration with life by adding medium definitions and
experiments. So you could add:

.. code-block:: yaml

    medium:
      path: "media/"
      definitions:
        m9_minimal:

which by default would look for a medium file ``media/m9_minimal.csv``.
Definition keys need to be valid YAML keys. In addition to CSV, other data
formats such as TSV, XLS or XLSX are also allowed. You can specify the filename
which also allows you to use a different name, although that would probably be
confusing.

.. code-block:: yaml

    medium:
      path: "media/"
      definitions:
        m9_minimal:
            filename: "minimal.xls"

Additionally, you can add a convenient label.

.. code-block:: yaml

    medium:
      path: "media/"
      definitions:
        m9_minimal:
            filename: "minimal.xls"
            label: "M9 minimal medium"

Format
------

A medium is defined by a tabular format with the following columns. A 'comment'
column is allowed for your own convenience but no entry is required.

========== ======== =========
 exchange   uptake   comment
========== ======== =========
 EX_glc_e       10
========== ======== =========

Each row must include the exchange reaction identifier and an uptake rate
between 0 and 1000.

Growth
======

Growth data are included under the key ``experiments:``. It works similarly to
media but allows a few extra definitions.

.. code-block:: yaml

    growth:
      path: "growth/"
      experiments:
        my_growth:
          filename: "my_growth.csv"
          medium: m9_minimal
          objective: Biomass
          label: "Exhaustive carbon growth"

Again, each experiment should have a unique key. By default, memote will look
for a relative CSV file of the same name. The specified medium refers to a
medium key. The objective, for the moment, should refer to a reaction identifier
such as that of the biomass reaction or ATP formation. Again, a more expressive
label can be given.

Only the experiment key is really required as the default filename, medium, and
objective may be used. However, growth data typically vary the carbon source
which is not reflected by the default medium. This will become more clear when
looking at the format.

Format
------

========== ======== ======== =========
 exchange   uptake   growth   comment
========== ======== ======== =========
 EX_glc_e       10     yes
 EX_glc_e        0      no
========== ======== ======== =========

For the tabular growth data, each row represents one data point with a binary
outcome. In order to take full advantage of this format it makes sense to define
a minimal medium without any carbon source. That medium will be used as the
basis and the exchange specified in each row of a growth experiment will be set
in addition to the base medium. **That means if you rely on the default medium
you will likely end up with multiple carbon sources.** The binary outcome in the
'growth' column will be compared to the model predictions. Any one of the
following values is recognized: "true", "True", "TRUE", "1", "yes", "Yes", "YES"
and "false", "False", "FALSE", "0", "no", "No", "NO".

Essentiality
============

Essentiality experiments can be defined in the same way as growth experiments
but the medium entry is interpreted differently.

.. code-block:: yaml

    essentiality:
      path: "essentiality/"
      experiments:
        knockouts:
          filename: "knockouts.xls"
          medium: glucose
          objective: Biomass
          label: "knock-out library"

Unlike for growth experiments, in the case of essentiality experiments the same
medium is used in each individual gene deletion experiment. If you have
knock-out experiments performed in different media, simply define the media and
define one essentiality experiment for each medium.

Format
------

======= =========== =========
 gene   essential   comment
======= =========== =========
 b0025      yes
======= =========== =========

An essentiality table should define unique gene identifiers as they are
specified in the model. At the moment, only single gene deletion experiments are
supported. The binary column 'essential' allows the same values as the 'growth'
column above. Again, *in silico* deletion outcomes are compared to the provided
ones.
