.. highlight:: shell

============
Installation
============

**Please Note**: With its
`retirement on the horizon <https://pythonclock.org>`_ we decided to stop
testing against Python 2.7,
and `like many others <https://python3statement.org>`_, want to focus entirely
on Python 3.
Hence, we cannot guarantee that the `memote` will still function as expected


Before installing memote, make sure that you have correctly installed the
latest version of `git`_.

We highly recommend creating a Python `virtualenv`_ for your model testing
purposes.

.. _virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs/
.. _git: https://git-scm.com/

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
