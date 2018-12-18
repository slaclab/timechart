import random

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QMessageBox

from pydm.utilities.colors import svg_color_from_hex

# If TimeChart is importing a StripTool config file, which contains a list of preferred colors, TimeChart will populate
# the STRIPTOOL_PREDEFINED_COLORS list. When TimeChart picks a random color for a curve, it'll pick from
# STRIPTOOL_PREDEFINED_COLORS instead of the predefined colors of TimeChart's own.
#
# On the other hand, if TimeChart imports its own JSON config file, it'll pick a random color for a curve from its
# own color list.
global STRIPTOOL_PREDEFINED_COLORS
STRIPTOOL_PREDEFINED_COLORS = []


PREDEFINED_COLORS = (QColor(Qt.red), QColor(Qt.green),  QColor(Qt.darkRed),  QColor(Qt.blue), QColor(Qt.darkGreen),
                     QColor(Qt.cyan), QColor(Qt.darkCyan), QColor(Qt.magenta), QColor(Qt.darkMagenta),
                     QColor(255, 0, 127), QColor(0, 85, 255), QColor(255, 85, 0), QColor(0, 170, 127),
                     QColor(0, 170, 255), QColor(85, 170, 255), QColor(255, 170, 0), QColor(255, 170, 255))


def add_striptool_color(color):
    STRIPTOOL_PREDEFINED_COLORS.append(color)


def random_color(curve_colors_only=False):
    """
    Return a QColor object from a predefined list.

    Parameters
    ----------
    curve_colors_only : bool
        If True, exclude black or white as the randomized color since a curve could be blended into the background. If
        False, include black or white as one of the randomized colors.

    Returns
    -------
    A color object randomly selected from the predefined list, and is not a white or black color if this is a color
    purported for a curve.
    """
    color_pick = pick_random_color()
    while curve_colors_only and color_pick in (QColor("black"), QColor("white")):
        color_pick = pick_random_color()

    return color_pick


def pick_random_color():
    """
    Straight-up pick a random color, with affinity given to the StripTool-predefined colors.

    Returns : QColor
    -------
    A color object randomly selected from the predefined list.
    """
    if len(STRIPTOOL_PREDEFINED_COLORS) > 0:
        return random.choice(STRIPTOOL_PREDEFINED_COLORS)
    else:
        return random.choice(PREDEFINED_COLORS)


def serialize_colors(timechart_settings):
    """
    Helper method to serialize QColor objects to string, useful for dumping converted contents into
    a JSON file.

    Parameters
    ----------
    timechart_settings : OrderDict
        The dictionary containing the converted configuration data.
    """
    for k, v in timechart_settings.items():
        if isinstance(timechart_settings[k], dict):
            serialize_colors(timechart_settings[k])
        elif "color" in k and v is not None:
            timechart_settings[k] = str(svg_color_from_hex(v.name(), hex_on_fail=True))


def display_message_box(icon, window_title, text):
    """
    Display a message box to the user, usually to inform the user of an invalid input value.

    Parameters
    ----------
    icon : QIcon
        The icon to display in the message box, i.e. Warning, Error, Info, etc.
    window_title : str
        The title of the message box window
    text : str
        The message to show to the user
    """
    msg_box = QMessageBox()
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(window_title)
    msg_box.setText(text)

    msg_box.exec_()

