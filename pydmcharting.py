from setup_paths import setup_paths
setup_paths()

import sys
import os

from arg_parser import ArgParser
from version import VERSION
import traceback

from pydm import PyDMApplication
from pydmcharting_logging import logging
from displays.main_display import PyDMChartingDisplay

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    _parse_arguments()

    app = PyDMApplication(command_line_args=sys.argv, hide_nav_bar=True, hide_menu_bar=True, hide_status_bar=True,
                          use_main_window=False)

    pydm_chartsdipslay = PyDMChartingDisplay()
    pydm_chartsdipslay.setMinimumSize(1600, 800)
    pydm_chartsdipslay.show()

    sys.exit(app.exec_())


def _parse_arguments():
    """
    Parse the command arguments.

    Returns
    -------
    The command arguments as a dictionary : dict
    """
    parser = ArgParser(description="A charting tool.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--version", action="version", version=VERSION)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.error("Unexpected exception during the charting process. Exception type: {0}. Exception: {1}"
                     .format(type(error), error))
        traceback.print_exc()
        for h in logger.handlers:
            h.flush()
