.. role:: red
.. role:: green
.. role:: blue

=========================
Understanding the reports
=========================

Memote will return one of four possible outputs.
If your preferred workflow is to benchmark one or several genome-scale
metabolic models (GSM) memote generates either a snapshot or a diff report,
respectively. For the reconstruction workflow the primary output is a history
report. This will only work if the provided input models are formatted
correctly in the systems biology markup language (SBML_). However, if a
provided model is not a valid SBML file, memote composes a report
enumerating errors and warnings from the SBML validator in
order of appearance. To better understand the output of the error report we
refer the reader to this section of the `SBML documentation`_. In this section
we will focus on how to understand the snapshot, diff and history reports.

.. _SBML: http://sbml.org/Main_Page
.. _SBML documentation: http://sbml.org/Facilities/Documentation/Error_Categories

Orientation
===========

Toolbar
-------

In all three reports, the blue toolbar at the top shows (from left to right)
the memote logo, a button which expand/ collapses all test results, a button
which displays the readme and the github icon which links to memote's github
page. On the snapshot report, the toolbar will also display the identifier of
the tested GSM and a timestamp showing when the test run was initiated.

Main Body
---------

The main body of the reports is divided into an independent section to the left
and a specific section to the right.

The tests in the independent section are
agnostic of the type of modeled organism, preferred modeling paradigms,
the complexity of a genome-scale metabolic model (GSM) or the types of
identifiers that are used to describe its components. The tests in this section
focus on testing adherence to fundamental principles of
constraint-based modeling: mass, charge and stoichiometric balance as well as
the presence of annotations. The results in this section can be normalized, and
thus enable a comparison of GSMs. The `Score_` at the bottom
of the page summarises the results to further simplify comparison.

The specific section on the right provides model specific statistics
and covers aspects of a metabolic network that can not be normalized
without introducing bias. For instance, dedicated quality control of the biomass
equation only applies to GSMs which are used to investigate cell growth, i.e.,
those for which a biomass equation has been generated. Some tests in this
section are also influenced by whether the tested GSM represents a prokaryote or
a eukaryote. Therefore the results cannot be generalized and direct comparisons
ought to take bias into account.

Test Results
------------

Test results are arranged in rows with the title visible to the left and the
result on the right. The result is displayed as white text in a coloured
rectangle detailed in `Color_`.

By default only the minimum information is visible as indicated by an arrow pointing
down right of the result. Clicking anywhere in the row will expand the result
revealing a description of the concept behind the test, its implementation
and a brief summary of the result.
In addition, there is a text field which contains plaintext representations of
Python objects which can be copy/pasted into Python code for follow up
procedures.

Some tests carry out one operation on several parameters and therefore deviate
slightly from the descriptions above. Expanding the title row reveals only the
description, while rows of the individual parameters reveal the text fields.

In the history report, instead of text fields scatterplots show how the
respective metrics developed over the commit history for each branch of a
repository. By clicking an entry in the legend, it is possible to toggle
its visibility in the plot.

Interpretation
==============

The variety of constraints-based modeling approaches and differences between
various organisms compound the assessment of GSMs. While memote facilitates
model assessment it can only do so within limitations. Please bear in mind the
diversity of Paradigms_ that challenge some of memote's results.

Color
-----

**Snapshot Report**

Results without highlights are kept in the main :blue:`blue` color of the memote
color scheme. Scored results will be marked with a gradient ranging from :red:`red`
to :green:`green` denoting a low or a high score respectively:

.. raw:: html

    <embed>
    <div>
    <span> <b>0%</b></span>
    <div style="display: inline-block; vertical-align: middle">
    <svg width="120" height="60">
    <defs>
    <linearGradient id="grad1">
    <stop offset="0%" style="stop-color:rgb(161, 18, 18);stop-opacity:1" />
    <stop offset="100%" style="stop-color:rgb(18, 161, 46);stop-opacity:1" />
    </linearGradient>
    </defs>
    <rect fill="url(#grad1)" x="10" y="10" width="100" height="100"/>
    </svg>
    </div>
    <span> <b>100% </b></span>
    </div>
    <br>
    </embed>

**Diff Report**

The colour in the Diff Report depends on the ratio of the sample minimum to
the sample maxium. Result sets where the sample minimum and the sample
maximum are identical will be coloured in the main blue colour of the
memote colour scheme. Result sets where the sample minimum is very small
relative to the sample maximum will appear red . This ratio is calculated
using :math:`1 - (Min / Max)) * 100`.

This is then mapped to the following gradient:

.. raw:: html

    <embed>
    <div>
    <span> <b>Identical</b></span>
    <div style="display: inline-block; vertical-align: middle">
    <svg width="120" height="60">
    <defs>
    <linearGradient id="grad1">
    <stop offset="0%" style="stop-color:rgb(42, 123, 184);stop-opacity:1" />
    <stop offset="100%" style="stop-color:rgb(161, 18, 18);stop-opacity:1" />
    </linearGradient>
    </defs>
    <rect fill="url(#grad1)" x="10" y="10" width="100" height="100"/>
    </svg>
    </div>
    <span> <b>Different </b></span>
    </div>
    <br>
    </embed>

Score
-----

Each test in the independent section provides a relative measure of
completeness with regard to the tested property. The final score is the
weighted sum of all individual test results normalized by the maximally
achievable score, i.e., all individual results at 100%. Individual tests can
be weighted, but it is also possible to apply weighting to entire test
categories. Hence the final score is calculated:

.. raw:: html

    <embed>
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 310 23">
    <defs>
      <symbol id="a" overflow="visible">
        <path d="M4.25-6.05c.08-.28.1-.34.23-.37.1-.02.43-.02.63-.02 1.01 0 1.45.03 1.45.82 0 .15-.03.54-.08.8l-.03.18c0 .06.03.14.13.14s.12-.08.15-.23L7-6.47c.02-.05.02-.14.02-.17 0-.11-.1-.11-.27-.11H1.22c-.24 0-.25.02-.33.2L.3-4.8c0 .02-.06.16-.06.2 0 .04.07.1.13.1.1 0 .1-.06.17-.22.53-1.55.8-1.72 2.27-1.72h.39c.28 0 .28.03.28.13 0 .04-.03.17-.05.2L2.1-.78C2-.42 1.97-.31.91-.31c-.36 0-.43 0-.43.18C.48 0 .6 0 .66 0l.8-.02.87-.01.83.01.86.02c.09 0 .21 0 .21-.2 0-.11-.07-.11-.34-.11-.23 0-.37 0-.62-.02-.3-.03-.38-.06-.38-.22 0-.01 0-.06.05-.2zm0 0"/>
      </symbol>
      <symbol id="b" overflow="visible">
        <path d="M4.67-2.72c0-1.05-.69-1.69-1.6-1.69C1.76-4.4.42-2.98.42-1.58.4-.59 1.08.11 2 .11c1.33 0 2.67-1.38 2.67-2.83zM2.02-.1c-.44 0-.88-.31-.88-1.1 0-.48.27-1.56.58-2.06.5-.76 1.08-.92 1.36-.92.58 0 .87.49.87 1.08 0 .4-.2 1.44-.58 2.08-.35.58-.9.92-1.35.92zm0 0"/>
      </symbol>
      <symbol id="c" overflow="visible">
        <path d="M2.05-3.98h.93c.2 0 .32 0 .32-.2 0-.12-.11-.12-.28-.12h-.88c.36-1.42.4-1.6.4-1.67 0-.17-.12-.26-.29-.26-.03 0-.31 0-.4.36L1.48-4.3H.53c-.2 0-.3 0-.3.2 0 .12.08.12.29.12h.87C.67-1.16.63-.98.63-.81c0 .54.37.92.92.92 1.01 0 1.57-1.45 1.57-1.53 0-.11-.07-.11-.1-.11-.1 0-.11.03-.16.14C2.44-.34 1.9-.11 1.56-.11c-.2 0-.31-.12-.31-.45 0-.25.03-.31.06-.49zm0 0"/>
      </symbol>
      <symbol id="d" overflow="visible">
        <path d="M3.72-3.77c-.19-.37-.47-.64-.92-.64C1.64-4.4.4-2.94.4-1.48.4-.55.96.1 1.73.1c.2 0 .7-.05 1.3-.75.07.42.43.75.9.75.36 0 .58-.23.75-.55.16-.36.3-.97.3-.98 0-.11-.1-.11-.13-.11-.09 0-.1.05-.14.19-.17.64-.34 1.23-.75 1.23-.28 0-.3-.27-.3-.45 0-.22.02-.31.13-.75.11-.4.13-.52.22-.9l.36-1.38c.06-.29.06-.3.06-.35 0-.17-.1-.26-.28-.26-.25 0-.39.22-.42.43zm-.64 2.58c-.06.19-.06.2-.2.38-.44.54-.85.7-1.13.7-.5 0-.64-.55-.64-.94 0-.5.31-1.72.55-2.18.3-.58.75-.96 1.15-.96.64 0 .78.82.78.88 0 .06-.01.12-.03.17zm0 0"/>
      </symbol>
      <symbol id="e" overflow="visible">
        <path d="M2.58-6.81s0-.11-.14-.11c-.22 0-.96.08-1.22.1-.08 0-.19.02-.19.21 0 .11.11.11.25.11.49 0 .5.1.5.17l-.03.2L.48-1.13a.97.97 0 0 0-.04.33c0 .58.43.92.9.92.33 0 .58-.2.75-.56.18-.38.3-.96.3-.97 0-.11-.1-.11-.12-.11-.1 0-.11.05-.13.19-.17.64-.36 1.23-.77 1.23-.3 0-.3-.31-.3-.45 0-.25.02-.3.07-.49zm0 0"/>
      </symbol>
      <symbol id="f" overflow="visible">
        <path d="M6.44-6.92c0-.03-.03-.11-.13-.11-.04 0-.04.01-.17.16l-.48.56c-.25-.47-.77-.72-1.43-.72-1.26 0-2.45 1.16-2.45 2.36 0 .8.52 1.26 1.03 1.4l1.06.29c.38.09.93.25.93 1.06C4.8-1.03 3.98-.1 3-.1c-.64 0-1.75-.22-1.75-1.46 0-.23.06-.48.06-.53l.02-.08c0-.09-.06-.1-.11-.1a.14.14 0 0 0-.11.04C1.08-2.19.5.1.5.13c0 .04.05.09.11.09C.68.22.7.2.82.06L1.3-.5c.42.58 1.1.72 1.68.72 1.36 0 2.54-1.33 2.54-2.56 0-.7-.35-1.04-.49-1.18-.23-.21-.39-.26-1.26-.48l-.68-.19a.93.93 0 0 1-.6-.9c0-.82.8-1.66 1.74-1.66.82 0 1.43.44 1.43 1.55 0 .3-.04.5-.04.56 0 0 0 .1.11.1s.13-.04.16-.21zm0 0"/>
      </symbol>
      <symbol id="g" overflow="visible">
        <path d="M3.95-3.78c-.17 0-.3 0-.43.12a.53.53 0 0 0-.2.4c0 .24.2.35.38.35.28 0 .55-.25.55-.64 0-.48-.47-.86-1.17-.86C1.73-4.4.4-2.98.4-1.58.4-.68.98.11 2.03.11 3.45.1 4.28-.95 4.28-1.06c0-.06-.05-.14-.1-.14-.07 0-.09.03-.15.1-.78 1-1.87 1-1.98 1-.63 0-.9-.5-.9-1.1 0-.4.2-1.38.54-1.99.31-.58.86-1 1.4-1 .33 0 .72.13.86.4zm0 0"/>
      </symbol>
      <symbol id="h" overflow="visible">
        <path d="M.88-.6l-.1.44c0 .18.14.27.3.27.12 0 .3-.08.37-.28.02-.03.35-1.4.4-1.58.07-.33.26-1.02.3-1.3.05-.12.33-.6.57-.8.08-.07.37-.34.8-.34.26 0 .4.13.42.13-.3.04-.52.28-.52.54 0 .16.11.35.38.35.26 0 .54-.24.54-.6 0-.34-.3-.64-.82-.64-.65 0-1.08.49-1.27.77a.92.92 0 0 0-.92-.77c-.46 0-.64.4-.74.57-.17.34-.3.93-.3.96 0 .11.1.11.12.11.1 0 .1-.01.17-.23.17-.7.37-1.19.73-1.19.16 0 .3.08.3.46 0 .21-.03.32-.16.84zm0 0"/>
      </symbol>
      <symbol id="i" overflow="visible">
        <path d="M1.86-2.3c.3 0 1.03-.03 1.53-.23.7-.3.75-.9.75-1.03 0-.44-.37-.85-1.06-.85-1.11 0-2.63.97-2.63 2.72 0 1.02.6 1.8 1.58 1.8C3.45.1 4.28-.95 4.28-1.06c0-.06-.05-.14-.1-.14-.07 0-.09.03-.15.1-.78 1-1.87 1-1.98 1-.78 0-.88-.85-.88-1.17 0-.12.02-.42.16-1.03zm-.47-.22c.4-1.51 1.42-1.67 1.69-1.67.45 0 .73.3.73.63 0 1.04-1.6 1.04-2.01 1.04zm0 0"/>
      </symbol>
      <symbol id="t" overflow="visible">
        <path d="M4.6-3.38c.06-.21.15-.59.15-.65 0-.17-.14-.27-.28-.27-.13 0-.3.08-.38.28-.03.07-.5 1.97-.56 2.24a2.34 2.34 0 0 0-.08.83c-.23.53-.53.84-.92.84-.8 0-.8-.73-.8-.9 0-.32.05-.7.52-1.94.1-.3.17-.44.17-.64a.8.8 0 0 0-.81-.82C.66-4.4.3-2.95.3-2.87c0 .1.1.1.1.1.12 0 .12-.03.16-.18.28-.92.66-1.24 1.02-1.24.1 0 .25.02.25.33 0 .25-.11.53-.19.7a6.08 6.08 0 0 0-.55 2.02C1.1-.24 1.75.1 2.5.1c.17 0 .64 0 1.03-.7.27.64.95.7 1.25.7.75 0 1.19-.63 1.45-1.22.33-.78.66-2.12.66-2.6 0-.54-.26-.7-.44-.7-.25 0-.5.27-.5.49 0 .12.07.19.14.26.11.11.36.36.36.85a5.9 5.9 0 0 1-.54 1.83c-.25.53-.61.87-1.1.87-.47 0-.73-.3-.73-.87 0-.27.06-.58.1-.72zm0 0"/>
      </symbol>
      <symbol id="u" overflow="visible">
        <path d="M2.83-6.23c0-.2-.14-.36-.36-.36-.28 0-.55.26-.55.53 0 .18.14.36.38.36.23 0 .53-.24.53-.53zm-.75 3.75c.1-.29.1-.32.22-.58.08-.2.12-.35.12-.53a.79.79 0 0 0-.81-.82C.67-4.4.3-2.95.3-2.87c0 .1.1.1.1.1.12 0 .12-.03.16-.18.28-.94.67-1.24 1.02-1.24.08 0 .25 0 .25.32 0 .21-.08.42-.11.53-.08.25-.53 1.4-.69 1.84-.1.25-.23.58-.23.8 0 .47.34.8.8.8.95 0 1.32-1.43 1.32-1.52 0-.11-.1-.11-.12-.11-.1 0-.1.03-.14.19-.2.62-.52 1.23-1.02 1.23-.17 0-.25-.1-.25-.33 0-.25.06-.39.3-1zm0 0"/>
      </symbol>
      <symbol id="v" overflow="visible">
        <path d="M4.69-3.77c.01-.04.03-.1.03-.17 0-.17-.11-.26-.28-.26-.1 0-.38.06-.4.42-.2-.36-.54-.63-.95-.63C1.97-4.4.73-3 .73-1.58.73-.59 1.33 0 2.05 0c.6 0 1.06-.47 1.15-.58l.02.02C3.02.3 2.89.74 2.89.75c-.05.1-.37 1.08-1.44 1.08-.18 0-.51-.02-.8-.11.3-.08.41-.34.41-.52 0-.15-.1-.34-.37-.34a.55.55 0 0 0-.53.58c0 .4.36.6 1.3.6 1.26 0 1.98-.77 2.13-1.37zM3.4-1.28c-.07.26-.3.51-.52.7-.2.17-.52.36-.81.36-.5 0-.64-.51-.64-.92 0-.47.28-1.66.56-2.16.27-.48.69-.89 1.1-.89.67 0 .8.82.8.86 0 .05 0 .11-.02.14zm0 0"/>
      </symbol>
      <symbol id="w" overflow="visible">
        <path d="M2.86-6.81s0-.11-.13-.11c-.23 0-.95.08-1.21.1-.08 0-.2.02-.2.2 0 .12.1.12.24.12.49 0 .5.06.5.17l-.03.2L.6-.38c-.04.14-.04.16-.04.22 0 .23.2.28.3.28a.4.4 0 0 0 .35-.27l.2-.75.2-.89.18-.67c.02-.06.11-.39.11-.45.03-.1.34-.64.69-.92.22-.16.51-.35.95-.35.42 0 .53.35.53.7 0 .54-.37 1.63-.6 2.24-.08.22-.15.34-.15.55 0 .47.36.8.83.8.94 0 1.3-1.44 1.3-1.52 0-.11-.08-.11-.11-.11-.11 0-.11.03-.16.19-.14.53-.47 1.23-1.01 1.23-.18 0-.24-.1-.24-.33 0-.25.08-.48.17-.7.16-.44.61-1.63.61-2.2 0-.64-.39-1.07-1.14-1.07-.62 0-1.1.32-1.48.77zm0 0"/>
      </symbol>
      <symbol id="A" overflow="visible">
        <path d="M3.9-3.73c-.27.01-.48.23-.48.45 0 .14.1.3.31.3.22 0 .46-.18.46-.57C4.19-4 3.77-4.4 3-4.4c-1.31 0-1.69 1.02-1.69 1.46 0 .78.74.92 1.03.98.52.11 1.04.22 1.04.77 0 .25-.22 1.1-1.43 1.1-.14 0-.9 0-1.14-.54.4.05.64-.25.64-.53 0-.22-.17-.35-.37-.35-.27 0-.56.2-.56.66 0 .56.57.97 1.42.97 1.62 0 2.01-1.2 2.01-1.66 0-.36-.18-.6-.3-.72-.27-.28-.57-.34-1-.42-.37-.08-.76-.15-.76-.6 0-.29.24-.9 1.11-.9.25 0 .75.08.9.46zm0 0"/>
      </symbol>
      <symbol id="C" overflow="visible">
        <path d="M9.23-6.05c.1-.36.11-.45.86-.45.22 0 .32 0 .32-.2 0-.11-.1-.11-.27-.11H8.83c-.27 0-.28 0-.4.18L4.8-.92l-.78-5.65c-.04-.23-.05-.23-.32-.23H2.34c-.18 0-.3 0-.3.18 0 .13.1.13.29.13l.44.02c.15.03.21.04.21.17l-.04.18-1.27 5.07c-.1.4-.26.72-1.08.75-.04 0-.17.01-.17.18 0 .1.06.13.14.13.31 0 .66-.03 1-.03L2.58 0c.04 0 .19 0 .19-.2 0-.11-.11-.11-.2-.11-.55 0-.66-.2-.66-.44 0-.06 0-.13.03-.23L3.3-6.41h.01l.86 6.18c.02.12.03.23.14.23.11 0 .17-.1.22-.17l4.03-6.31h.02L7.14-.78c-.1.39-.1.47-.9.47-.16 0-.27 0-.27.18 0 .13.1.13.14.13l1.23-.03L8.6 0c.07 0 .2 0 .2-.2 0-.11-.1-.11-.29-.11-.36 0-.64 0-.64-.17 0-.05 0-.07.05-.25zm0 0"/>
      </symbol>
      <symbol id="D" overflow="visible">
        <path d="M3.33-3.02c.06-.25.3-1.17.98-1.17a1 1 0 0 1 .5.13.58.58 0 0 0-.47.54c0 .16.11.35.38.35.22 0 .53-.17.53-.58 0-.52-.58-.66-.92-.66-.58 0-.92.54-1.05.75A1.1 1.1 0 0 0 2.2-4.4C1.17-4.4.6-3.12.6-2.87c0 .1.1.1.12.1.08 0 .1-.03.12-.1.35-1.07 1-1.32 1.35-1.32.19 0 .53.1.53.67 0 .32-.17.97-.53 2.38-.16.6-.52 1.03-.96 1.03-.06 0-.28 0-.5-.12.25-.07.47-.27.47-.55 0-.27-.22-.34-.36-.34-.3 0-.54.25-.54.57 0 .46.48.66.92.66.67 0 1.03-.7 1.05-.75.12.36.48.75 1.07.75 1.04 0 1.6-1.28 1.6-1.53 0-.11-.08-.11-.11-.11-.1 0-.11.05-.14.1C4.36-.33 3.69-.1 3.37-.1c-.39 0-.54-.31-.54-.66 0-.21.04-.43.15-.87zm0 0"/>
      </symbol>
      <symbol id="j" overflow="visible">
        <path d="M6.84-3.27c.16 0 .35 0 .35-.18 0-.2-.19-.2-.33-.2H.89c-.14 0-.33 0-.33.2 0 .18.19.18.33.18zm.02 1.94c.14 0 .33 0 .33-.2 0-.19-.19-.19-.35-.19H.9c-.14 0-.33 0-.33.19 0 .2.19.2.33.2zm0 0"/>
      </symbol>
      <symbol id="y" overflow="visible">
        <path d="M3.3 2.4c0-.04 0-.06-.17-.23C1.89.92 1.55-.97 1.55-2.5c0-1.73.38-3.47 1.61-4.7.13-.13.13-.14.13-.17 0-.08-.03-.11-.1-.11-.1 0-1 .68-1.6 1.95-.5 1.1-.62 2.2-.62 3.03 0 .78.11 1.98.66 3.13A4.37 4.37 0 0 0 3.2 2.5c.07 0 .1-.03.1-.1zm0 0"/>
      </symbol>
      <symbol id="B" overflow="visible">
        <path d="M2.88-2.5c0-.77-.11-1.97-.66-3.1A4.39 4.39 0 0 0 .67-7.49a.1.1 0 0 0-.1.1c0 .04 0 .05.18.24.98.98 1.55 2.56 1.55 4.64C2.3-.78 1.94.97.7 2.22c-.14.12-.14.14-.14.17 0 .06.05.11.11.11.1 0 1-.69 1.58-1.95.52-1.1.63-2.2.63-3.05zm0 0"/>
      </symbol>
      <symbol id="k" overflow="visible">
        <path d="M4.2 5.33L.66 9.7c-.08.1-.1.11-.1.16 0 .1.1.1.28.1H9.1l.86-2.48H9.7a2.7 2.7 0 0 1-1.76 1.64c-.16.07-.85.3-2.32.3H1.4l3.47-4.28c.06-.1.08-.1.08-.16 0-.04 0-.04-.07-.14L1.65.41h3.94C6.72.4 9.02.47 9.7 2.33h.25L9.1 0H.84C.56 0 .56.02.56.31zm0 0"/>
      </symbol>
      <symbol id="l" overflow="visible">
        <path d="M4.95-4.81c0-.03-.03-.1-.1-.1-.04 0-.04.02-.13.11l-.34.4c-.27-.38-.7-.5-1.13-.5-.98 0-1.86.8-1.86 1.6 0 .1.03.38.24.64.23.27.5.33.96.46.14.03.49.1.6.14.22.04.64.2.64.72 0 .56-.6 1.23-1.38 1.23-.62 0-1.36-.22-1.36-.98 0-.08.02-.24.05-.36v-.03c0-.1-.08-.1-.1-.1-.1 0-.12.02-.13.14L.55-.04C.53-.03.52.01.52.05c0 .03.03.08.1.08.04 0 .05-.02.15-.1l.32-.38c.38.4.91.48 1.33.48 1.06 0 1.9-.9 1.9-1.73 0-.3-.12-.58-.27-.74-.24-.25-.35-.28-1.25-.5l-.44-.1c-.17-.07-.47-.24-.47-.63 0-.56.63-1.11 1.34-1.11.77 0 1.13.42 1.13 1.08l-.03.3c0 .12.08.12.12.12.1 0 .11-.05.13-.16zm0 0"/>
      </symbol>
      <symbol id="m" overflow="visible">
        <path d="M1.56-1.6c.19 0 .75 0 1.13-.13.51-.2.6-.52.6-.72 0-.4-.38-.63-.85-.63-.85 0-1.97.64-1.97 1.85 0 .7.44 1.3 1.25 1.3 1.19 0 1.73-.7 1.73-.79 0-.05-.06-.12-.12-.12-.03 0-.05.01-.11.07-.55.65-1.36.65-1.49.65-.42 0-.7-.29-.7-.85 0-.1 0-.23.1-.62zm-.39-.18c.3-1.02 1.06-1.1 1.27-1.1.3 0 .56.16.56.43 0 .67-1.19.67-1.48.67zm0 0"/>
      </symbol>
      <symbol id="n" overflow="visible">
        <path d="M3.05-2.67c-.25.04-.35.23-.35.39 0 .19.14.26.27.26.15 0 .39-.1.39-.45 0-.47-.53-.6-.9-.6-1.05 0-2.02.96-2.02 1.93 0 .6.4 1.2 1.28 1.2 1.19 0 1.73-.69 1.73-.78 0-.05-.06-.12-.12-.12-.03 0-.05.01-.11.07-.55.65-1.36.65-1.49.65-.5 0-.71-.35-.71-.79 0-.18.09-.95.45-1.43.26-.35.62-.54.98-.54.1 0 .42.02.6.2zm0 0"/>
      </symbol>
      <symbol id="o" overflow="visible">
        <path d="M1.72-2.75h.7c.14 0 .22 0 .22-.16 0-.09-.08-.09-.2-.09h-.66l.25-1.03a.32.32 0 0 0 .03-.1c0-.14-.1-.23-.25-.23-.17 0-.26.13-.33.3-.04.18.05-.16-.26 1.06h-.7C.39-3 .3-3 .3-2.84c0 .09.08.09.2.09h.66L.75-1.11c-.05.17-.1.42-.1.52 0 .4.35.65.74.65C2.17.06 2.61-.9 2.61-1c0-.1-.1-.1-.11-.1-.1 0-.1.02-.16.15-.18.43-.54.82-.92.82-.15 0-.25-.09-.25-.34 0-.06.03-.22.05-.28zm0 0"/>
      </symbol>
      <symbol id="p" overflow="visible">
        <path d="M2.27-4.36c0-.1-.1-.26-.29-.26-.18 0-.39.18-.39.39 0 .1.08.26.28.26s.4-.2.4-.39zM.84-.8c-.03.1-.06.17-.06.3 0 .32.27.57.66.57.69 0 1-.95 1-1.06 0-.1-.1-.1-.11-.1-.1 0-.11.05-.14.13-.16.56-.46.84-.74.84-.14 0-.17-.09-.17-.24 0-.16.05-.29.11-.44l.22-.56c.06-.18.33-.8.34-.9A.5.5 0 0 0 2-2.48c0-.33-.28-.6-.66-.6C.64-3.08.33-2.12.33-2c0 .08.1.08.12.08.1 0 .1-.03.13-.11.17-.6.48-.85.73-.85.11 0 .17.05.17.24 0 .17-.03.27-.2.7zm0 0"/>
      </symbol>
      <symbol id="q" overflow="visible">
        <path d="M3.7-1.86c0-.76-.58-1.22-1.26-1.22-1.03 0-2 .97-2 1.92C.44-.46.94.06 1.7.06c1 0 2-.9 2-1.92zm-2 1.74c-.34 0-.68-.22-.68-.79 0-.28.12-.96.4-1.36.3-.43.7-.6 1.02-.6.37 0 .69.25.69.76 0 .17-.08.86-.4 1.34-.26.43-.67.65-1.03.65zm0 0"/>
      </symbol>
      <symbol id="r" overflow="visible">
        <path d="M.84-.44c-.01.1-.06.27-.06.28 0 .16.13.22.24.22.12 0 .23-.08.28-.14.03-.06.07-.3.12-.44l.14-.62c.05-.16.1-.31.13-.47.08-.28.1-.34.3-.62.18-.29.51-.65 1.04-.65.4 0 .4.36.4.49 0 .42-.29 1.19-.4 1.48-.08.2-.1.27-.1.38 0 .37.29.6.65.6.7 0 1-.96 1-1.07 0-.1-.08-.1-.11-.1-.1 0-.1.05-.13.13-.15.56-.46.84-.73.84-.16 0-.19-.09-.19-.24 0-.16.05-.26.17-.57.08-.22.36-.95.36-1.34 0-.67-.53-.8-.9-.8-.58 0-.97.36-1.17.64-.05-.48-.46-.64-.75-.64-.3 0-.46.22-.55.38-.16.26-.25.65-.25.7 0 .08.1.08.12.08.1 0 .1-.02.14-.2.11-.41.25-.75.52-.75.19 0 .23.15.23.34 0 .12-.06.39-.12.58l-.14.62zm0 0"/>
      </symbol>
      <symbol id="s" overflow="visible">
        <path d="M3-2.63c-.17.05-.3.2-.3.33 0 .17.14.24.24.24.08 0 .34-.05.34-.4 0-.46-.5-.62-.94-.62-1.07 0-1.28.81-1.28 1.02 0 .26.16.44.25.51.17.14.3.18.78.25.16.03.6.11.6.46 0 .12-.08.39-.36.56-.28.16-.63.16-.7.16-.29 0-.68-.07-.85-.3.24-.03.4-.2.4-.4 0-.16-.13-.26-.27-.26C.7-1.08.5-.9.5-.6c0 .42.44.67 1.1.67 1.3 0 1.54-.87 1.54-1.14 0-.64-.7-.76-.97-.81l-.28-.06c-.25-.05-.37-.2-.37-.35 0-.15.12-.34.28-.45.18-.1.42-.13.54-.13.14 0 .5.02.66.25zm0 0"/>
      </symbol>
      <symbol id="z" overflow="visible">
        <path d="M3.4-4.22c.04-.2.05-.22.2-.23h.42c.43 0 .6 0 .78.04.3.1.33.3.33.55 0 .11 0 .2-.05.56l-.02.08c0 .08.05.11.13.11.1 0 .1-.06.12-.17l.19-1.33c0-.1-.08-.1-.2-.1H1.02c-.18 0-.2 0-.24.15L.33-3.33.3-3.2c0 .03.01.1.12.1.1 0 .1-.04.14-.18.4-1.11.64-1.17 1.7-1.17h.29c.22 0 .22 0 .22.06 0 0 0 .05-.04.14L1.81-.58c-.06.25-.08.33-.81.33-.25 0-.31 0-.31.16C.69-.08.7 0 .8 0l.6-.02L2-.03l.64.01.58.02c.06 0 .15 0 .15-.16 0-.09-.06-.09-.28-.09l-.4-.02c-.24-.01-.25-.04-.25-.12 0-.06 0-.06.03-.17zm0 0"/>
      </symbol>
      <symbol id="x" overflow="visible">
        <path d="M3.88-2.77L1.89-4.75c-.12-.13-.14-.14-.22-.14a.2.2 0 0 0-.2.2c0 .07.01.08.12.19l2 2-2 2.02c-.1.1-.12.12-.12.18 0 .13.1.2.2.2.08 0 .1 0 .22-.13l1.99-1.99L5.94-.16c.01.02.08.07.14.07.12 0 .2-.08.2-.2 0-.02 0-.05-.03-.12-.02-.01-1.6-1.57-2.1-2.09l1.83-1.81c.05-.07.2-.19.25-.25 0-.02.05-.07.05-.13 0-.12-.08-.2-.2-.2-.08 0-.11.03-.22.14zm0 0"/>
      </symbol>
    </defs>
    <use x=".11" y="15.07" xlink:href="#a"/>
    <use x="7.32" y="15.07" xlink:href="#b"/>
    <use x="12.15" y="15.07" xlink:href="#c"/>
    <use x="15.75" y="15.07" xlink:href="#d"/>
    <use x="21.02" y="15.07" xlink:href="#e"/>
    <use x="24.19" y="15.07" xlink:href="#f"/>
    <use x="30.87" y="15.07" xlink:href="#g"/>
    <use x="35.18" y="15.07" xlink:href="#b"/>
    <use x="40.02" y="15.07" xlink:href="#h"/>
    <use x="44.79" y="15.07" xlink:href="#i"/>
    <use x="52.18" y="15.07" xlink:href="#j"/>
    <use x="63.89" y=".73" xlink:href="#k"/>
    <use x="74.41" y="11.19" xlink:href="#l"/>
    <use x="79.68" y="11.19" xlink:href="#m"/>
    <use x="83.46" y="11.19" xlink:href="#n"/>
    <use x="87.02" y="11.19" xlink:href="#o"/>
    <use x="90.03" y="11.19" xlink:href="#p"/>
    <use x="92.85" y="11.19" xlink:href="#q"/>
    <use x="96.78" y="11.19" xlink:href="#r"/>
    <use x="101.7" y="11.19" xlink:href="#s"/>
    <use x="107.62" y="8.2" xlink:href="#t"/>
    <use x="115.02" y="8.2" xlink:href="#i"/>
    <use x="119.66" y="8.2" xlink:href="#u"/>
    <use x="123.09" y="8.2" xlink:href="#v"/>
    <use x="128.2" y="8.2" xlink:href="#w"/>
    <use x="133.94" y="8.2" xlink:href="#c"/>
    <use x="137.54" y="9.69" xlink:href="#s"/>
    <use x="141.3" y="9.69" xlink:href="#m"/>
    <use x="145.08" y="9.69" xlink:href="#n"/>
    <use x="148.65" y="9.69" xlink:href="#o"/>
    <use x="151.65" y="9.69" xlink:href="#p"/>
    <use x="154.47" y="9.69" xlink:href="#q"/>
    <use x="158.4" y="9.69" xlink:href="#r"/>
    <use x="166.04" y="8.2" xlink:href="#x"/>
    <use x="176" y="8.2" xlink:href="#y"/>
    <use x="179.87" y=".73" xlink:href="#k"/>
    <use x="190.39" y="11.19" xlink:href="#z"/>
    <use x="196.17" y="11.19" xlink:href="#m"/>
    <use x="199.95" y="11.19" xlink:href="#s"/>
    <use x="203.71" y="11.19" xlink:href="#o"/>
    <use x="206.71" y="11.19" xlink:href="#s"/>
    <use x="212.64" y="8.2" xlink:href="#t"/>
    <use x="220.03" y="8.2" xlink:href="#i"/>
    <use x="224.67" y="8.2" xlink:href="#u"/>
    <use x="228.1" y="8.2" xlink:href="#v"/>
    <use x="233.21" y="8.2" xlink:href="#w"/>
    <use x="238.95" y="8.2" xlink:href="#c"/>
    <use x="242.55" y="9.69" xlink:href="#o"/>
    <use x="245.56" y="9.69" xlink:href="#m"/>
    <use x="249.34" y="9.69" xlink:href="#s"/>
    <use x="253.1" y="9.69" xlink:href="#o"/>
    <use x="258.82" y="8.2" xlink:href="#x"/>
    <use x="268.79" y="8.2" xlink:href="#A"/>
    <use x="273.46" y="8.2" xlink:href="#g"/>
    <use x="277.77" y="8.2" xlink:href="#b"/>
    <use x="282.6" y="8.2" xlink:href="#h"/>
    <use x="287.37" y="8.2" xlink:href="#i"/>
    <use x="292.01" y="9.69" xlink:href="#o"/>
    <use x="295.01" y="9.69" xlink:href="#m"/>
    <use x="298.79" y="9.69" xlink:href="#s"/>
    <g>
      <use x="302.56" y="9.69" xlink:href="#o"/>
    </g>
    <g>
      <use x="306.07" y="8.2" xlink:href="#B"/>
    </g>
    <path fill="none" stroke="#000" stroke-miterlimit="10" stroke-width=".405" d="M63.89 12.58h246.06"/>
    <g>
      <use x="163.44" y="21.91" xlink:href="#C"/>
    </g>
    <g>
      <use x="174.2" y="21.91" xlink:href="#d"/>
    </g>
    <g>
      <use x="179.46" y="21.91" xlink:href="#D"/>
    </g>
    <g>
      <use x="185.16" y="21.91" xlink:href="#f"/>
    </g>
    <g>
      <use x="191.85" y="21.91" xlink:href="#g"/>
    </g>
    <g>
      <use x="196.16" y="21.91" xlink:href="#b"/>
    </g>
    <g>
      <use x="200.99" y="21.91" xlink:href="#h"/>
    </g>
    <g>
      <use x="205.76" y="21.91" xlink:href="#i"/>
    </g>
    </svg>
    </embed>


Weights for sections and individual tests are indicated by a white number
inside a magenta badge. No badge means that the weight defaults to 1.



Paradigms
=========

"Reconstructions" and "Models"
------------------------------

Some authors may publish metabolic networks which are parameterized,
ready to run flux balance analysis (FBA), these are referred to simply as
'models'. Alternatively, others may publish unconstrained metabolic knowledgebases
(referred to as 'reconstructions'), from which several models can be derived
by applying different constraints. Both can be encoded in SBML. With having
an independent test section, we attempt to make both 'models' and
'reconstructions' comparable, although a user should be aware that this
difference exists and is subject to `some discussion`_. Please note, that some
tests in the specific section may error for a reconstruction as they
require initialization.

.. _some discussion: https://github.com/opencobra/memote/issues/228

"Lumped" and "Split" Biomass Reaction
-------------------------------------

There are two basic ways of specifying the biomass composition. The most
common is a single lumped reaction containing all biomass precursors.
Alternatively, the biomass equation can be split into several reactions
each focusing on a different macromolecular component for instance
a (1 gDW ash) + b (1 gDW phospholipids) + c (free fatty acids)+
d (1 gDW carbs) + e (1 gDW protein) + f (1 gDW RNA) + g (1 gDW DNA) +
h (vitamins/cofactors) + xATP + xH2O-> 1 gDCW biomass + xADP + xH + xPi. The
benefit of either approach depends very much on the use cases which are
`discussed by the community`_. Memote employs heuristics to identify the type
of biomass which may fail to distinguish edge cases.

.. _discussed by the community: https://github.com/opencobra/memote/issues/243

"Average" and "Unique" Metabolites
-----------------------------------------

A metabolite consisting of a fixed core with variable branches such as a
membrane lipid are sometimes implemented by averaging over the distribution of
individual lipid species. The resulting pseudo-metabolite is assigned an
average chemical formula, which requires scaling of stoichiometries of
associated reactions to avoid floating point numbers in the chemical formulae.
An alternative approach is to implement each species as a distinct
metabolite in the model, which increases the total count of reactions. Memote
cannot yet distinguish between these paradigms, which means that results
in the specific sections that rely on the total number of reactions or scaling
of stochiometric parameters may be biased.
