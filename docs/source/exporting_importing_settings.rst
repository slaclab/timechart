=================================
Exporting and Importing Settings
=================================


*******************
Exporting Settings
*******************

TimeChart's settings can be saved into a file, which can be imported in TimeChart's next run.

To save TimeChart's settings into a file, click on the Export Button below the Chart Canvas. This will bring up the
Export Chart Data dialog:


    .. image:: images/export.png
       :width: 300px
       :height: 250px
       :scale: 100%
       :alt: TimeChart's Export Dialog
       :align: center


    * Under the Export Options list, select Chart Settings
    * Check the ``Include currently plotted PVs`` to save the current PVs into the config file if you want TimeChart
      to plot these PVs immediately the next time it runs
    * Check the ``Include current chart settings`` to save the rest of TimeChart's customized settings
    * Click on the Export Button to select the location to save the file. The file will be saved in the JSON format,
      which can be viewed and edited in a text editor.

        .. important::
            It is recommended that you do not modify the config file manually as the JSON format can be error-prone.
            You should always create a TimeChart config file using the Export feature of TimeChart.


.. _importing settings:

*******************
Importing Settings
*******************

There are two ways to import TimeChart's settings from a config file:

#. From the command line, use the ``--config-file {path_to_config_file}`` command line parameter::


        timechart --config-file ../config_files/timechart_config.json

        or

        timechart --config-file ../config_files/striptool_config.stp


#. Alternatively, from the TimeChart UI, click the Import Button, and open either a TimeChart JSON config file, or a StripTool STP file.