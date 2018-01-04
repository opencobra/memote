.. highlight:: shell

===============
Getting Started
===============

Installation
============

We highly recommend creating a Python `virtualenv`_ for your model testing
purposes.

.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Stable release
--------------

To install memote, run this command in your terminal:

.. code-block:: console

    $ pip install memote

This is the preferred method to install memote, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io/en/stable/
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

From sources
------------

The sources for memote can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone https://github.com/opencobra/memote.git

Or download the `tarball
<https://github.com/opencobra/memote/archive/master.tar.gz>`_ or
`zip <https://github.com/opencobra/memote/archive/master.zip>`_ archive:

.. code-block:: console

    $ curl  -OL https://github.com/opencobra/memote/archive/master.zip

Once you have a copy of the source files, you can install it with:

.. code-block:: console

    $ pip install .


.. _Github repo: https://github.com/opencobra/memote


After installation, memote can be employed in two different ways: As a
benchmarking tool for ad hoc model assessment and as an automated testing
suite to aid
with the reconstruction of metabolic models. When using memote to benchmark a
model, the tests are run once and a report is generated which describes the
status-quo.
As an automated testing suite, memote facilitates tracking incremental model
changes in a version controlled repository and can enable continuous testing and
reporting if desired.

Here, we explain step-by-step the necessary commands to pursue either workflow.
Users that have already followed this tutorial once may want to refer to the
:doc:`cheat-sheet flowchart <flowchart>` to refresh their memory.

Benchmark
=========

Single Model
------------

To benchmark the performance of a single model, run this command in your
terminal:

.. code-block:: console

    $ memote report snapshot path/to/model.xml

This will generate the performance report as ``index.html``.

The output filename can be changed by adding the following option.
To illustrate here it is changed to ``report.html``.

.. code-block:: console

    $ memote report snapshot --filename "report.html" path/to/model.xml

While the html report is still a work in progress, we recommend relying on the
verbose output of the command line tool above. Users can tweak the console
output by passing additional arguments directly to pytest through the
``--pytest-args`` or simply ``-a`` option. This can be done by
writing the pytest arguments as one continuous string.

For a more detailed traceback try:

.. code-block:: console

    $ memote report snapshot -a "--tb long" --filename "report.html" path/to/model.xml

For a full list of possible arguments please refer to the `pytest
documentation`_.

.. _pytest documentation: https://docs.pytest.org/en/latest/usage.html

Comparative
-----------

**This functionality is coming soon.**

Comparing two models against each other and quickly identify the differences.

Reconstruction
==============

When starting a memote repository, users need to provide an SBMLv3-FBC formatted
file. Automatic draft reconstruction tools such as `Pathway Tools`_,
`Model SEED`_, `The RAVEN Toolbox`_ and `others`_ are able to output files in
this format. Model repositories such as `BiGG`_ or `BioModels`_ further serve
as a great resource for models in the correct format.

.. _Pathway Tools: http://www.pathwaytools.org/
.. _Model SEED: http://modelseed.org
.. _The RAVEN Toolbox: https://github.com/SysBioChalmers/RAVEN
.. _others: http://www.secondarymetabolites.org/sysbio/
.. _BiGG: http://bigg.ucsd.edu
.. _BioModels: https://www.ebi.ac.uk/biomodels/

With this in mind, starting a local, version-controlled model repository is as
simple as running the following command:

.. code-block:: console

    $ memote new

CI tested, online and public workflow:
--------------------------------------

After this, the user will be prompted with a few questions regarding details of
the project. If the project is to be kept strictly locally, the user does
not need to supply `GitHub`_ (or `GitLab`_ - not implemented yet) credentials.
However, these are a requirement if the project is to use the full benefits of
distributed version control such as cloud-based development, remote
collaboration and community feedback. It is important to note that furthermore
a public repository is needed to set up automatic testing through continuous
integration, one of the key features of memote.

Once all the questions following ``memote new`` have been answered, a public
repository has been created under either the user's GitHub or GitLab account.
To enable continuous integration via Travis CI the following command is
executed:

**This functionality is coming soon.** A manual workaround is outlined in the
`cookiecutter-memote readme <https://github.com/opencobra/cookiecutter-memote/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/README.md>`_.

.. code-block:: console

    $ memote online

Now, after each edit to the model in the repository, the user can generate
an update to the continuous model report shown at the project's gh-pages
branch by saving the changes with the following command:

**This functionality is coming soon, for now please utilize the steps outlined for advanced users.**

.. code-block:: console

    $ memote save

For advanced users: ``memote save`` is the equivalent of executing ``git add .``,
``git commit`` and ``git push`` in sequence.

Offline, local or private workflow:
-----------------------------------

Users that have decided to not to use `GitHub`_ (or `GitLab`_ **Not implemented yet**) or those that
have decided to set the model repository to private, will need to execute:

.. code-block:: console

    $ memote run

to run the testing suite on their commit history followed by:

.. code-block:: console

    $ memote report history

to generate the same type of report that would be shown automatically with
continuous integration. After this it is crucial to save the generated test
results by running ``memote save`` again.

We recommend the public workflow not only to promote open, collaborative
science but also to benefit from the full functionality of memote.

.. _GitHub: https://github.com
.. _GitLab: https://gitlab.com
