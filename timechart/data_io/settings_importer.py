# Configuration Data Importing, for Both TimeChart and StripTool Configuration Files

from .import_strategies.settings_import_strategy import SettingsImportException
from .import_strategies.timechart_import_strategy import TimeChartImportStrategy
from .import_strategies.striptool_import_strategy import StripToolImportStrategy

import logging
logger = logging.getLogger(__name__)


class SettingsImporter:
    """
    Import configuration data from files exported from different sources, i.e. TimeChart and
    StripTool.
    """
    def __init__(self, pydm_main_display):
        """
        Parameters
        ----------
        pydm_main_display : PyDMDisplay
            The Main Window object.
        """
        self._import_strategies = (TimeChartImportStrategy(pydm_main_display),
                                   StripToolImportStrategy(pydm_main_display))

    def import_settings(self, filename):
        """
        Switch conversion strategies to import a configuration file into TimeChart until running out
        of known conversion strategies.

        Parameters
        ----------
        filename : The path to a configuration data file.
        """
        successful_conversion = False

        for i in range(len(self._import_strategies)):
            if not successful_conversion:
                try:
                    self._import_strategies[i].import_file(filename)
                    successful_conversion = True
                except SettingsImportException as error:
                    logger.debug("Importing failed with '{0}'. Error: {1}. Switching to the next conversion "
                                 "strategy...".format(type(self._import_strategies[i]).__name__, error))
                except Exception as error:
                    logger.exception("Cannot import the settings file '{0}'. "
                                     "Error: {1}".format(filename, error))
        if not successful_conversion:
            logger.exception("Importing the setting file '{0}' failed. Make sure there is a "
                             "conversion method for the file format.".format(filename))
