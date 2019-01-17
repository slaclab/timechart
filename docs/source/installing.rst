=====================
Installing TimeChart
=====================


.. _prerequisites:

**************
Prerequisites
**************

At the minimum, you will need:

* Python 2.7, or 3.5+ (3.6+ recommended)
* PyDM >= 1.6.0
* numpy >= 1.11.0
* qtpy
* pyqtgraph >= 0.10.0
* six

.. important::

    If your computer does not have Python, or your Python version does not meet the requirement, you
    must `update Python <https://www.python.org/downloads/>`_.

    To check the Python version::

        python --version

    You will also need to install ``git`` for the platform on which you are about to run TimeChart. Follow these
    `Git Installation Instructions <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.


***********
Installing
***********

.. _setuptools:

Using setuptools
=================
First, clone the TimeChart repository, and then run ``setup.py`` with the ``install`` option::

    git clone https://github.com/slaclab/timechart.git
    cd timechart
    python setup.py install


.. _conda:

Using conda
============
You must first install install `Miniconda <https://conda.io/miniconda.html>`_. Pick the Miniconda for Python 3.6+.

Then, use the ``conda`` command to install TimeChart::

    conda install timechart -c tidair-dev -c pydm-tag

    or

    conda install timechart -c tidair-tag -c pydm-tag

* `tidair-dev` has the latest development code
* `tidair-tag` has the latest stable released version (tag).


Using pip
===========
    .. important::

        Your computer may not have ``pip`` pre-installed. If that is the case, refer to the
        `pip Installation Instructions <https://pip.pypa.io/en/stable/installing/>`_ before proceeding.

        Some of TimeChart's requirements, such as ``numpy``, could run into conflict with an existing application's
        in your computer. You will have to resolve those conflicts while using ``pip``. If there are conflicts, the
        alternative could be that you run TimeChart in the Miniconda environment (see :ref:`conda`), or create a
        virtual environment (`virtualenv <https://virtualenv.pypa.io/en/latest/>`_) to install TimeChart in it.

For ``pip`` installation, you must first clone this TimeChart repository, and then run ``pip install``::

    git clone https://github.com/slaclab/timechart.git
    cd timechart
    pip install .[all]


In Development Environment
===========================
For developers, you can install TimeChart in development mode using ``setuptools``::


    git clone https://github.com/slaclab/timechart.git
    cd timechart
    python setup.py develop


If you want to build an Anaconda package for TimeChart::

    conda install conda-build anaconda-client
    conda update -q conda conda-build

    git clone https://github.com/slaclab/timechart.git
    cd timechart

    conda build -q conda-recipe --python=3.6 --output-folder bld-dir -c conda-forge -c pydm-tag -c conda-forge

Note that you must change the value of the parameter `python=...` to the Python version you are using.
