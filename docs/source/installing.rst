=====================
Installing TimeChart
=====================

.. _prerequisites:

**************
Prerequisites
**************

Python and Python Libraries
============================
* Python 2.7 (2.7.9+ recommended), or 3.5+ (3.6+ recommended)
* PyDM >= 1.6.0
* numpy >= 1.11.0
* qtpy
* pyqtgraph >= 0.10.0
* six

.. important::

    To check the Python version::

        python --version

    Note that if you have both Python 2 and Python 3 on your computer, and you want to check for the Python 3 version::

        python3 --version

    If your computer does not have Python, or your Python version does not meet the requirement, you
    must `install or update Python <https://www.python.org/downloads/>`_.

Operating Systems
=================
* Linux (tested on RHEL 6.10+, CentOS 7.5+)
* macOS (tested on High Sierra (10.13)+)


.. _obtain the TimeChart source code:

************************************
Obtaining the TimeChart Source Code
************************************

Unless you are going to install TimeChart with conda (see :ref:`using conda`), the rest of the installation options
require you to either download or clone the TimeChart source code from GitHub.


Downloading the Stable Release Source Code
===========================================

You can download the source code of one of TimeChart's stable releases from the `GitHub TimeChart Release page
<https://github.com/slaclab/timechart/releases>`_. Make sure you unzip or untar the downloaded file into a separate
directory.

In all the examples below, it is assumed that that directory's name is ``timechart``.


Cloning the Source Code
========================

.. important::
    If you opt to clone the TimeChart source code from GitHub, you will also need to install ``git`` for the
    platform on which you are about to run TimeChart. Follow these
    `Git Installation Instructions <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_ to install ``git``.

#. Clone the TimeChart repo::

    git clone https://github.com/slaclab/timechart.git

#. If you want to build TimeChart with the latest code, you can stop here. Otherwise, to build TimeChart with source
   code from a stable release, you will need to check out a release tag::

    git checkout <tag>

For example, if you want to build TimeChart with the stable release
`v1.2.2 <https://github.com/slaclab/timechart/releases/tag/v1.2.2>`_, use this command::

    git checkout v1.2.2

Now, you can proceed to installing TimeChart.


***********
Installing
***********

.. _setuptools:

Using setuptools
=================
#. First, you must perform the steps in :ref:`obtain the TimeChart source code`
#. Then, run ``setup.py`` with the ``install`` option::

    cd timechart
    python setup.py install


.. important::
    If you have both Python 2 and Python 3 installed on your computer, and you want to run TimeChart with Python 3,
    use the command ``python3 setup.py install`` instead.


.. _using conda:

Using conda
============
You do not have to obtain the TimeChart source code with this installation option.

#. You must first install `Miniconda <https://conda.io/miniconda.html>`_. Pick the Miniconda for Python 3.6+.
#. Then, use the ``conda`` command to install TimeChart::

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
        alternative could be that you run TimeChart in the Miniconda environment (see :ref:`Using conda`), or create a
        virtual environment (`virtualenv <https://virtualenv.pypa.io/en/latest/>`_) to install TimeChart in it.

#. First, you must perform the steps in :ref:`obtain the TimeChart source code`
#. Then, run ``pip install``::

    cd timechart
    pip install .

.. important::
    If you have both Python 2 and Python 3 installed on your computer, and you want to run TimeChart with Python 2,
    use ``pip install .``. If you want to run TimeChart with Python 3 instead, run the ``pip3 install .`` command.


In Development Environment
===========================
For developers, you can install TimeChart in development mode using ``setuptools``.

#. First, you must perform the steps in :ref:`obtain the TimeChart source code`
#. Then, run ``setup.py`` with the ``develop`` option::

    cd timechart
    python setup.py develop


.. important::
    If you have both Python 2 and Python 3 installed on your computer, and you want to run TimeChart with Python 3,
    use the command ``python3 setup.py develop`` instead.

If you want to build an Anaconda package for TimeChart:

#. First, you must perform the steps in :ref:`obtain the TimeChart source code`
#. Next, install `Miniconda <https://conda.io/miniconda.html>`_. Pick the Miniconda build for Python 3.6+.
#. Finally, issue the following commands::

    cd timechart
    conda install conda-build anaconda-client
    conda update -q conda conda-build
    conda build -q conda-recipe --python=3.6 --output-folder bld-dir -c conda-forge -c pydm-tag -c conda-forge

Note that you must change the value of the parameter ``python=...`` to the Python version you are using.


*************
Uninstalling
*************

You can uninstall TimeChart by using this command::

    pip uninstall timechart

.. important::
    If you have both Python 2 and Python 3 installed on your computer, and you want to run TimeChart with Python 2,
    use ``pip uninstall timechart``. If you want to run TimeChart with Python 3 instead, run the
    ``pip3 uninstall timechart`` command.
