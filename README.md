<img src="timechart_launcher/icons/charts_128.png" width="128" height="128" align="right"/>
  <h1>TimeChart</h1>
  <h3>A Charting Tool based on PyDM</h3>
</p>

TimeChart is a Python Qt-based graphing application for control systems.
It is intended to be the modern, feature-by-feature matching alternative
to the Motif [EPICS Strip Tool](https://epics.anl.gov/extensions/StripTool/ "EPICS Strip Tool") application.

Comparing with Strip Tool, TimeChart possesses the inherent cross-platform,
responsive, and regularly maintained and supported advantages offered by
[Python Display Manager (PyDM)](https://github.com/slaclab/pydm "PyDM").
As a Python Qt-based framework, PyDM is also created and maintained by SLAC.
Its charting capability is built upon [pyqtgraph](http://pyqtgraph.org/ "PyQtGraph"),
and the PyDM's TimePlot is the central widget in TimeChart.

# Prerequisites
* Python 2.7 or 3.5
* PyDM >= 1.4.0

Python package requirements are listed in the requirements.txt file, which can
be used to install all requirements from pip: 'pip install -r requirements.txt'

# Installing TimeChart
You must first install PyDM as it is the framework TimeChart is built upon.
In doing so, you must first satisfy the [PyDM prerequisites](https://github.com/slaclab/pydm/blob/master/requirements.txt, "PyDM Requirements"):
 
```sh
git clone https://github.com/slaclab/pydm.git
cd pydm
pip install .[all]
```

Next, clone this TimeChart repository:

```sh
git clone https://github.com/slaclab/timechart.git
cd timechart
pip install .[all]
```

# Running TimeChart
After installing TimeChart, you can start the application:

```timechart```

For developers, you can install TimeChart in development mode:

```sh
git clone https://github.com/slaclab/timechart.git
cd timechart
python setup.py develop
timechart
```

# Acknowledgements

Icons made by [monkik](https://www.flaticon.com/authors/monkik) from [www.flaticon.com](https://www.flaticon.com/) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/).
