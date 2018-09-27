import sys
import traceback
import argparse
import logging

from pydm.application import PyDMApplication

import timechart
from timechart.displays.main_display import PyDMChartingDisplay


def main():
    args, extra_args = _parse_arguments()

    logger = logging.getLogger('')
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if args.log_level:
        logger.setLevel(args.log_level)
        handler.setLevel(args.log_level)

    app = PyDMApplication(hide_nav_bar=True, hide_menu_bar=True, hide_status_bar=True, use_main_window=False)

    display = PyDMChartingDisplay(args=extra_args)
    display.show()

    sys.exit(app.exec_())


def _parse_arguments():
    """
    Parse the command arguments.

    Returns
    -------
    The command arguments as a dictionary : dict
    """

    parser = argparse.ArgumentParser(
        description="A charting tool based on the Python Display Manager (PyDM).")

    parser.add_argument(
        '--log_level',
        help='Configure level of log display',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO'
        )

    parser.add_argument('--version', action='version',
                        version='PyDMCharting {version}'.format(
                            version=timechart.__version__))

    args, extra_args = parser.parse_known_args()
    return args, extra_args


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        traceback.print_exc()
