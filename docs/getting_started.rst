.. highlight:: shell

===============
Getting Started
===============

After installation, memote can be employed in two different ways: As a
benchmarking tool for ad hoc performance testing, and as a testing suite to aid
with the reconstruction of metabolic models. When using memote to benchmark a
model, the tests are run once and a report is generated which depicts the
status-quo. Opposed to this, memote as a testing suite sets up a
version-controlled repository, enables continuous integration via Travis CI and
produces a performance report with each incremental change.

Here, we explain step by step the necessary commands to pursue either workflow.
Users that have already followed this tutorial once may want to refer to the
:doc:`cheat-sheet flowchart <flowchart>` to refresh their memory.

Benchmark
---------

Single Model
^^^^^^^^^^^^

To benchmark the performance of a single model, run this command in your
terminal:

.. code-block:: console

    $ memote --model path/to/model.xml report --one-time

This will generate the performance report as index.html

The output filename can be changed by adding the following option.
To illustrate here it is changed to 'report.html'.

.. code-block:: console

    $ memote --model path/to/model.xml report --one-time --filename "report.html"

Comparative
^^^^^^^^^^^

**This functionality is coming soon**

Benchmarking one model against another is done by running the following
command:

.. code-block:: console

    $ memote --model path/to/model.xml report --diff path/to/model2.xml

Reconstruction
--------------

When starting a memote repository, users need to provide a SBMLv3-FBC formatted
.xml file. Automatic draft reconstruction tools such as `Pathway Tools`_,
`Model SEED`_, `The RAVEN Toolbox`_ and `others`_ are able to output files in
this format. Model repositories such as `BiGG`_ or `BioModels`_ further serve
as a great resource for models in the correct format.

.. _Pathway Tools: http://bioinformatics.ai.sri.com/ptools/
.. _Model SEED: http://modelseed.org
.. _The RAVEN Toolbox: https://github.com/SysBioChalmers/RAVEN
.. _others: http://www.secondarymetabolites.org/sysbio/
.. _BiGG: http://bigg.ucsd.edu
.. _BioModels: https://www.ebi.ac.uk/biomodels-main/

With this in mind, starting a local, version-controlled model repository is as
simple as running the following command:

.. code-block:: console

    $ memote new

CI tested, online and public workflow:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After this, the user will be prompted with a few questions regarding details of
the project. If the project is to be kept strictly locally, the user does
not need to supply `GitHub`_ (or `GitLab`_ - not implemented yet) credentials.
However, these are a requirement if the project is to use the full benefits of
distributed version control such as cloud-based development, remote
collaboration and community feedback. It is important to note that furthermore
a public repository is needed to set up automatic testing through continuous
integration, one of the key features of memote.

Once all the questions following `memote new` have been answered, a public
repository has been created under either the user's GitHub or GitLab account.
To enable continuous integration via Travis CI the following command is
executed:

**This functionality is coming soon, a manual workaround is outlined in the `cookiecutter-memote readme`_**
.. code-block:: console

    $ memote online

Now, after each edit to the model in the repository, the user can generate
an update to the continuous model report shown at the project's gh-pages
branch by saving the changes with the following command:

**This functionality is coming soon, for now please utilize the steps outlined for advanced users**
.. code-block:: console

    $ memote save

For advanced users: `memote save` is the equivalent of executing `git add`,
`git commit` and `git push` in sequence.

.. _cookiecutter-memote readme: https://github.com/opencobra/cookiecutter-memote

Offline, local or private workflow:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Users that have decided to not to use `GitHub`_ (or `GitLab`_ **Not implemented yet**) or those that
have decided to set the model repository to private, will need to execute:

.. code-block:: console

    $ memote

to run the testing suite on their commit history followed by:

.. code-block:: console

    $ memote report

to generate the same type of report that would be shown automatically with
continuous integration. After this it is crucial to save the generated test
results by running `memote save` again.

We recommend the public workflow not only to promote open, collaborative
science but also to benefit from the full functionality of memote.

.. _GitHub: https://github.com
.. _GitLab: https://gitlab.com
