=====================
Installing TimeChart
=====================


.. _prerequisites:

**************
Prerequisites
**************

* Python 2.7, or 3.5+ (3.6+ recommended)
* PyDM >= 1.6.0

Python package requirements are listed in the `requirements.txt` file, which can be used to install all requirements
from pip: `pip install -r requirements.txt`

You will also need to install ``git`` for the platform on which you are about to run TimeChart.

***********
Installing
***********

Using pip
===========
First, clone this TimeChart repository, and then start ``pip install``::

    git clone https://github.com/slaclab/timechart.git
    cd timechart
    pip install .[all]


Using conda
============
You can install TimeChart for the conda environment::

    conda install timechart -c tidair-dev -c pydm-tag

    or

    conda install timechart -c tidair-tag -c pydm-tag

* `tidair-dev` has the latest development code
* `tidair-tag` has the latest stable released version (tag).


In Development Environment
===========================
For developers, you can install TimeChart in development mode::


    git clone https://github.com/slaclab/timechart.git
    cd timechart
    python setup.py develop


If you want to build an Anaconda package for TimeChart:

#. Install `Miniconda <https://conda.io/miniconda.html>`_. Pick the Miniconda for Python 3.6+
#. Run the following commands:::

    conda install conda-build anaconda-client
    conda update -q conda conda-build

    git clone https://github.com/slaclab/timechart.git
    cd timechart

    conda build -q conda-recipe --python=3.6 --output-folder bld-dir -c conda-forge -c pydm-tag -c conda-forge

Note that you must change the value of the parameter `python=...` to the Python version you are using.
