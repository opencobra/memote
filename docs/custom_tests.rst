.. highlight:: shell

============
Custom Tests
============

Memote can be configured to include custom test modules from any other directory
in addition to the tests that are included in the package.

Custom Test Setup
=================

All custom test modules and the tests defined inside of them have to adhere to
the same standard design for the results to be generated and displayed correctly.
Optionally, a user may specify a configuration file which can be used to
change how individual tests are displayed in the snapshot report.

A Custom Test Module
--------------------

At its core, a memote test module is a collection of specific python code in a
text file with the file ending ``.py``. Since, memote uses `pytest <https://docs.pytest.org/en/latest/>`_ for discovery
and execution of model tests, the `conditions`_ for memote test modules and
pytest test modules are identical.

The module name has to match either ``test_*.py`` or ``*_test.py``:

.. _conditions: https://docs.pytest.org/en/latest/goodpractices.html#test-package-name

.. code-block:: console

    your_custom_directory/
        test_module1.py
        module2_test.py
        ...

Minimal Test Module & Simple Test Function Template
---------------------------------------------------

The minimal content of a custom test module should look like this:

.. code-block:: python

    import pytest
    from memote.utils import annotate, wrapper, truncate

    import path.to.your_support_module as your_support_module


    @annotate(
        title="Some human-readable descriptive title for the report",
        type="Single keyword describing how the data ought to be displayed."
    )
    def test_your_custom_case(read_only_model):
    """
    Docstring that briefly outlines the test function.

    A more elaborate explanation of why this test is important, how it works,
    and the assumptions/ theory behind it. This can be more than one line.
    """
    ann = test_your_custom_case.annotation
    ann["data"] = list(your_support_module.specific_model_quality(read_only_model))
    ann["metric"] = len(ann["data"]) / len(read_only_model.reactions)
    ann["message"] = wrapper.fill(
        """A concise message that displays and explains the test results.
        For instance, if data is a list of items the amount: {} and
        percentage ({:.2%}) values can be recorded here, as well as an
        excerpt of the list itself: {}""".format(
        len(ann["data"]), ann['metric'], truncate(ann['data'])
        ))
    )
    assert len(ann["data"]) == 0, ann["message"]


This is a minimal test module template containing a test function called
``test_your_custom_case``. There can be additional lines of code, but you
should keep in mind that any logic is best put into a separate support
module, which is imported above as ``your_support_module``. The functions of
this support module are called by the test function. This will simplify
debugging, error handling and allows for dedicated unit testing on the code
in the support module.

The following components are requirements of ``test_your_custom_case``:

- Each test has to be decoreated with the ``annotate()`` decorator, which
  collects:

  - The ``data`` that the test is run on. Can be of the following type: ``list``,
    ``set``, ``tuple``, ``string``, ``float``, ``integer`` and ``boolean``. It
    can be of type ``dictionary``, but this is only supported for parametrized
    tests (see example below).

  - The ``type`` of data. This is not the actual python type
    of ``data``! Choose it according to how you'd like the results to be
    displayed in the reports. For example: In the case above ``data``
    is a list, for instance it could be list of unbalanced reactions. If you choose
    ``type="length"``, the report will display its length. With ``type="array"``
    it will display the individual items of the list. If ``data`` is a
    single string then ``type="string"`` is best. In case, you'd rather display
    the ``metric`` as opposed to the contents of ``data`` use
    ``type="number"``. ``type="object"`` is only supported for parametrized
    tests (see example below).

  - A human-readable, descriptive ``title`` that will be displayed in the report
    as opposed to the test function name ``test_your_custom_case`` which will
    only serve as the test's ID internally.

  - ``metric`` can be any fraction relating to the quality that is tested. In
    memote's core tests the metrics of each scored tests are used to calculate
    the overall score.

  - The ``message`` is a brief summary of the results displayed only on the
    command line. There are no restrictions on what it should include. We've
    generally tried to keep this short and concise to avoid spamming the command
    line.

- The prefix 'test\_' is required by pytest for automatic test discovery.
  Every function with this prefix will be executed when later running memote
  with the configuration to find custom tests.

- ``read_only_model`` is the required parameter to access the loaded
  metabolic model.

- In the report the docstring is taken as a tooltip for each test. It should
  generally adhere to the `conventions`_ of the NumPy/SciPy documentation. It
  suffices to write a brief one-sentence outline of the test function optionally
  followed by a more elaborate explanation that helps the user to understand
  the test's purpose and function.

- The assert statement works just like the assert statement in `pytest <https://docs.pytest.org/en/latest/assert.html>`_.

.. _conventions: https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Parametrized Test Function Template
-----------------------------------
Pytest allows us to run one test function with `multiple sets of arguments`_ by
simply using the ``pytest.mark.paremtrize`` decorator. This is quite useful
when the same underlying assertion logic can be applied to several parameters.
In the following example taken from ``memote.suite.tests.test_annotation`` we test
that there are no metabolites that lack annotations from any of the databases
listed in ``annotation.METABOLITE_ANNOTATIONS``. Without parametrization we
would have had to copy the entire test function below to specifically check
the metabolite annotations for each database.

.. _multiple sets of arguments: https://docs.pytest.org/en/latest/parametrize.html#parametrize


.. code-block:: python

    @pytest.mark.parametrize("db", list(annotation.METABOLITE_ANNOTATIONS))
    @annotate(title="Missing Metabolite Annotations Per Database",
              type="object", message=dict(), data=dict(), metric=dict())
    def test_metabolite_annotation_overview(read_only_model, db):
        """
        Expect all metabolites to have annotations from common databases.

        The required databases are outlined in `annotation.py`.
        """
        ann = test_metabolite_annotation_overview.annotation
        ann["data"][db] = get_ids(annotation.generate_component_annotation_overview(
            read_only_model.metabolites, db))
        ann["metric"][db] = len(ann["data"][db]) / len(read_only_model.metabolites)
        ann["message"][db] = wrapper.fill(
            """The following {} metabolites ({:.2%}) lack annotation for {}:
            {}""".format(len(ann["data"][db]), ann["metric"][db], db,
                         truncate(ann["data"][db])))
        assert len(ann["data"][db]) == 0, ann["message"][db]


Custom Test Configuration
=========================

Finally, there are two ways of configuring memote to find custom tests. The
first involves the ``--custom`` option of the memote CLI and requires the user
to provide a corresponding config file with the custom test modules, while the second
involves passing arguments directly to pytest through the use of the
``--pytest-args`` option, which can be abbreviated to ``-a``. This option only
requires the user to set up the custom test module. No config file is needed
here.

The Custom Option
-----------------

When invoking the ``memote run`` or ``memote report snapshot`` commands in
the terminal, it is possible to add the ``--custom`` option. This option takes
two parameters in a fixed order:

1. The absolute path to any directory in which pytest is to check for custom
   tests modules. By default test discovery is recursive. More information is
   provided `here`_.

2. The absolute path to a valid configuration file.

.. _here: https://docs.pytest.org/en/latest/goodpractices.html

.. code-block:: console

    $ memote report snapshot --custom path/to/dir/ path/to/config.yml --filename "report.html" path/to/model.xml

The Pytest Option
-----------------

In case you want to avoid setting up a configuration file, it is possible to
pass any number of absolute paths to custom test directories directly to pytest,
as long as they are placed behind any other parameters that you might want to pass in.
For instance here we want to get a list of the ten slowest running tests while
including two custom test module directories:

.. code-block:: console

    $ memote run -a "--durations=10 path/to/dir1/ path/to/dir2/" --filename "report.html" path/to/model.xml
