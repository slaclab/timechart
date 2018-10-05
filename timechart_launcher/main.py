import os
import sys
import traceback
import argparse
import logging

import warnings
warnings.filterwarnings("ignore")

from pydm.application import PyDMApplication

from qtpy import QtGui, QtCore

import timechart
from timechart.displays.main_display import TimeChartDisplay


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

    base_path = os.path.dirname(os.path.realpath(__file__))
    icon_path_mask = os.path.join(base_path, "icons", "charts_{}.png")

    app = PyDMApplication(hide_nav_bar=True, hide_menu_bar=True,
                          hide_status_bar=True, use_main_window=False)

    app_icon = QtGui.QIcon()
    app_icon.addFile(icon_path_mask.format(16), QtCore.QSize(16, 16))
    app_icon.addFile(icon_path_mask.format(24), QtCore.QSize(24, 24))
    app_icon.addFile(icon_path_mask.format(32), QtCore.QSize(32, 32))
    app_icon.addFile(icon_path_mask.format(64), QtCore.QSize(64, 64))
    app_icon.addFile(icon_path_mask.format(128), QtCore.QSize(128, 128))
    app_icon.addFile(icon_path_mask.format(256), QtCore.QSize(256, 256))

    app.setWindowIcon(app_icon)
    display = TimeChartDisplay(args=extra_args)
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
                        version='TimeChart {version}'.format(
                            version=timechart.__version__))

    args, extra_args = parser.parse_known_args()
    return args, extra_args


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        traceback.print_exc()
