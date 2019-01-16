==================
Running TimeChart
==================

TimeChart can be started without or with startup parameters.


***************************
Without Startup Parameters
***************************

After installing TimeChart, you can start the application::

    timechart


************************
With Startup Parameters
************************

TimeChart can be started with startup parameters:

+-----------------------------------------+----------------------------------------+---------------------------------------------------+
| Parameters                              | Description                            | Example                                           |
|                                         |                                        |                                                   |
+=========================================+========================================+===================================================+
| ``--help`` or ``-h``                    | Show the help message and then exit    | ``timechart --help`` or ``./timechart -h``        |
+-----------------------------------------+----------------------------------------+---------------------------------------------------+
| ``--version``                           | Show the TimeChart version             | ``timechart --version``                           |
+-----------------------------------------+----------------------------------------+---------------------------------------------------+
| ``--config-file {path_to_config_file}`` | Start TimeChart with either a          | ``timechart --config-file timechart_config.json`` |
|                                         | TimeChart or StripTool config file     |                                                   |
|                                         |                                        | or                                                |
|                                         |                                        |                                                   |
|                                         |                                        | ``timechart --config-file striptool_config.stp``  |
|                                         |                                        |                                                   |
+-----------------------------------------+----------------------------------------+---------------------------------------------------+
