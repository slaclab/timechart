"""
Configuration Data Importing, for Both TimeChart and StripTool Configuration Files
"""

import six
import json

from .importers.timechart_config_importer import TimeChartConfigImporter
from .importers.striptool_config_importer import StripToolConfigImporter
from ..utilities.utils import serialize_colors


import logging
logger = logging.getLogger(__name__)


class SettingsImporterException(Exception):
    pass


class SettingsImporter:
    """
    Import configuration data from files exported from different sources, i.e. TimeChart and
    StripTool.
    """
    def __init__(self, pydm_main_display=None):
        """
        Parameters
        ----------
        pydm_main_display : PyDMDisplay
            The Main Window object.
        """
        self.timechart_importer = TimeChartConfigImporter(pydm_main_display)
        self.striptool_importer = StripToolConfigImporter(pydm_main_display)

    def import_settings(self, filename):
        """
        Import the settings from a file, which could be a TimeChart JSON file, or a StripTool .stp file.

        Parameters
        ----------
        filename : The path to a configuration data file.
        """
        try:
            with open(filename, 'r') as settings_file:
                if filename.endswith(".stp"):
                    logger.warning("The StripTool config file format will soon be unsupported. You can convert this "
                                   "file to the TimeChart config format by clicking on the Export button, then select "
                                   "Chart Settings while running TimeChart.")
                    timechart_settings = self.convert_stp_file(settings_file)
                else:
                    timechart_settings = json.load(settings_file)

            # Apply the settings as TimeChart settings, now that we have all the file data converted to the same
            # TimeChart config format
            self.timechart_importer.apply_settings(timechart_settings)
        except Exception as error:
            six.raise_from(SettingsImporterException(str(error)), error)

    def convert_stp_file(self, stp_file_handle, new_timechart_file=None):
        """
        Convert a StripTool STP file into the TimeChart config data, and write to a TimeChart JSON config file if
        requested.

        Parameters
        ----------
        stp_file_handle : io
            The handle to the STP config file
        new_timechart_file : str
            The full path to the TimeChart file to write the TimeChart config dict to.

        Returns
        -------
            The TimeChart settings dictionary.

        """
        # Parse the StripTool file
        stp_data = self.striptool_importer.import_to_dict(stp_file_handle)

        # Convert to the equivalent TimeChart settings
        timechart_settings = self.striptool_importer.convert_to_timechart_setting(stp_data)

        if new_timechart_file:
            serialize_colors(timechart_settings)

            with open(new_timechart_file, 'w') as output_file:
                json.dump(timechart_settings, fp=output_file, indent=4, separators=(',', ': '))

        return timechart_settings
