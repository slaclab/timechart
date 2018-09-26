# PyDMCharting: Python Display Manager Charting Tool
PyDMCharting is a Python Qt-based graphing application for control systems. It is intended to be the modern, feature-by-feature matching alternative to the Motif [EPICS Strip Tool](https://epics.anl.gov/extensions/StripTool/ "EPICS Strip Tool") application.

Comparing with Strip Tool, PyDMCharting possesses the inherent cross-platform, responsive, and regularly maintained and supported advantages offered by [Python Display Manager (PyDM)](https://github.com/slaclab/pydm "PyDM"). As a Python Qt-based framework, PyDM is also created and maintained by SLAC. Its charting capability is built upon [pyqtgraph](http://pyqtgraph.org/ "PyQtGraph"),
and the PyDM's TimePlot is the central widget in PyDMCharting.

# Prerequisites
* Python 2.7 or 3.5
* PyDM >= 1.4.0

Python package requirements are listed in the requirements.txt file, which can be used to install all requirements from pip: 'pip install -r requirements.txt'

# Installing PyDMCharting
You must first install PyDM as it is the framework PyDMCharting is built upon. In doing so, you must first satisfy the [PyDM prerequisites](https://github.com/slaclab/pydm/blob/master/requirements.txt, "PyDM Requirements"):
 
```sh
git clone https://github.com/slaclab/pydm.git
cd pydm
pip install .[all]
```

Next, clone this PyDMCharting depot:

```sh
git clone https://github.com/slaclab/pydmcharting.git
cd pydmcharting
pip install .[all]
```

# Running PyDMCharting
After installing PyDMCharting, make sure you export the following environment variables:

```
sh
export EPICS_CA_AUTO_ADDR=yes
export PYEPICS_LIBCA=<your path to libca.so>
```
The PYEIPCS_LIBCA path is required for Linux only.

```pydmcharting```

For developers, you can install PyDMCharting in development mode:

```sh
git clone https://github.com/slaclab/pydm.git
cd pydm
python setup.py develop
pydmcharting
```


