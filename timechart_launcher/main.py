import os
try:
    from os import errno
except ImportError:
    # For Python 3.7
    import errno

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

    try:
        os.makedirs("logs")
    except os.error as err:
        # It's OK if the log directory exists. This is to be compatible with Python 2.7
        if err.errno != errno.EEXIST:
            raise err

    logging.basicConfig(level=logging.INFO, filename=os.path.join("logs", "timechart.log"),
                        format="[%(asctime)s] [%(levelname)-8s] - %(message)s")

    logger = logging.getLogger('')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    if args.log_level:
        logger.setLevel(args.log_level)
        console_handler.setLevel(args.log_level)

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

    config_file = None
    if args.config_file:
        config_file = os.path.expandvars(os.path.expanduser(args.config_file))

    display = TimeChartDisplay(config_file=config_file, args=extra_args)
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

    parser.add_argument("--config-file",
                        help="The configuration file to import to and start TimeChart.")
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
