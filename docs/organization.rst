====================
Package Organization
====================

.. code-block::

  memote - memote - support - ...
                  - suite - tests - ...
                          - reporting - ...
         - tests - test_for_support

* ``memote/support/``:
  * Functions that perform checks on the model and return results.
* ``memote/suite/tests/``:
  * ``pytest`` functions that compare the output of ``memote/support/`` functions
    with expected values.
* ``tests/``:
  * ``pytest`` functions that ensure that ``memote/support/`` functions perform
    as expected.
