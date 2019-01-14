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
TimeChart also includes a conda recipe for building an installation package for the conda package management
environment::

    git clone https://github.com/slaclab/timechart.git
    cd timechart
    conda build -q conda-recipe --python=3.6 --output-folder bld-dir -c conda-forge -c pydm-tag -c conda-forge

This installation package then is ready to be uploaded to a conda channel for other users, who will only need to issue
the command::

    conda install timechart -c <channel_name>

to install TimeChart in the conda environment.


In Development Environment
===========================
For developers, you can install TimeChart in development mode::


    git clone https://github.com/slaclab/timechart.git
    cd timechart
    python setup.py develop
