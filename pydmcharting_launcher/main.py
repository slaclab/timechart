import sys

import versioneer
from arg_parser import ArgParser
import traceback

from pydm.application import PyDMApplication
from pydmcharting_logging import logging
from displays.main_display import PyDMChartingDisplay

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    _parse_arguments()

    app = PyDMApplication(command_line_args=sys.argv, hide_nav_bar=True, hide_menu_bar=True, hide_status_bar=True,
                          use_main_window=False)

    pydm_chartsdipslay = PyDMChartingDisplay()
    pydm_chartsdipslay.setMinimumSize(1200, 800)
    pydm_chartsdipslay.show()

    sys.exit(app.exec_())


def _parse_arguments():
    """
    Parse the command arguments.

    Returns
    -------
    The command arguments as a dictionary : dict
    """
    parser = ArgParser(description="A charting tool based on the Python Display Manager (PyDM).")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--version", action="version", version=versioneer.get_version())

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
