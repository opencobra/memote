.. highlight:: shell
.. _contributing:

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/opencobra/memote/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

memote could always use more documentation, whether as part of the
official memote docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/opencobra/memote/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `memote` for local development.

1. Fork the `memote` repo on GitHub.
2. Clone your fork locally::

    git clone git@github.com:your_name_here/memote.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    mkvirtualenv memote
    cd memote/
    pip install -e .

4. Create a branch for local development using ``fix`` or ``feat`` as a prefix::

    git checkout -b fix-name-of-your-bugfix

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and
   the tests, including testing other Python versions. This is all included
   with tox::

    tox

   You can run all tests in parallel using detox. To get tox and detox, just
   pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub. Please use `semantic
   commit messages <https://seesparkbox.com/foundry/semantic_commit_messages>`_::

    git add .
    git commit -m "fix: Your detailed description of your changes."
    git push origin fix-name-of-your-bugfix

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring.
3. The pull request should work for Python 2.7, 3.4, 3.5 and 3.6. Check
   https://travis-ci.org/opencobra/memote/pull_requests
   and make sure that the tests pass for all supported Python versions.
