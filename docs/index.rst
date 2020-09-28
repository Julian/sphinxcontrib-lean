.. include:: ../README.rst

Contents
--------

.. toctree::
    :glob:
    :maxdepth: 2


.. module:: sphinxcontrib.lean


Installation
------------

`sphinxcontrib.lean` may be installed from PyPI in the typical way, e.g.:

.. code-block:: sh

    $ pip install sphinxcontrib-lean

or by including it in the requirements file of your documentation.

To enable this extension, add `sphinxcontrib.lean` to the
:confval:`extensions <sphinx:extensions>` list of your `Sphinx
configuration file <sphinx:usage/configuration>`:

.. code-block:: python

    extensions = ["sphinxcontrib.lean"]


You may also wish to set the ``primary_domain`` setting to ``lean`` so
that you can omit the ``lean`` prefixes below.


Usage
-----

`sphinxcontrib.lean` includes directives for a number of Lean objects.

.. code-block:: rst

    .. lean:theorem:: number_theory.flt

        This documentation is too narrow to include a description of
        this theorem.

will be rendered as:

    .. lean:theorem:: number_theory.flt

        This documentation is too narrow to include a description of
        this theorem.
