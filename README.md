# PyDMCharting: Python Display Manager Charting Tool
PyDMCharting is a Python Qt-based graphing application for control systems. It is intended to be the modern, feature-by-feature matching alternative to the Motif [EPICS Strip Tool](https://epics.anl.gov/extensions/StripTool/ "EPICS Strip Tool") application.

Comparing with Strip Tool, PyDMCharting possesses the inherent cross-platform, responsive, and regularly maintained and supported advantages offered by [Python Display Manager (PyDM)](https://github.com/slaclab/pydm "PyDM"). As a Python Qt-based framework, PyDM is also created and maintained by SLAC. Its charting capability is built upon [pyqtgraph](http://pyqtgraph.org/ "PyQtGraph"),
and the PyDM's TimePlot is the central widget in PyDMCharting.

# Prerequisites
* Python 2.7 or 3.5
* PyDM >= 0.18

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
In the ```pydmcharting``` directory, customize the ```pydmcharting_setup.sh``` setup script to the paths appropriate to your system. At minimum, you will need to provide the following settings:

* Where to source the environment setup script for using PyDM. Example: ```source /afs/slac/g/lcls/package/pydm/setup_pydm_env.bash```
* The path to PyDM, exported as PYDM_PATH environment variable. Example: ```export PYDM_PATH=/u/re/hbui/local/dev/pydm```
* Linux only: the path to the EPICS libca.so library. Example: ```export PYEPICS_LIBCA=/afs/slac/g/lcls/epics/base/R3.15.5-1.0/lib/rhel6-x86_64/libca.so```
* Finally, if you plan to test PyDMCharting using PyDM's pydm-testing-ioc, you must ```export EPICS_CA_AUTO_ADDR_LIST=yes```

To run PyDMCharting:

```./PyDMCharting```

Note that the command is case-sensitive.


