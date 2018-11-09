import random

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QMessageBox


global STRIPTOOL_PREDEFINED_COLORS
STRIPTOOL_PREDEFINED_COLORS = []


PREDEFINED_COLORS = (QColor(Qt.red), QColor(Qt.green),  QColor(Qt.darkRed),  QColor(Qt.blue), QColor(Qt.darkGreen),
                     QColor(Qt.cyan), QColor(Qt.darkCyan), QColor(Qt.magenta), QColor(Qt.darkMagenta),
                     QColor(255, 0, 127), QColor(0, 85, 255), QColor(255, 85, 0), QColor(0, 170, 127),
                     QColor(0, 170, 255), QColor(85, 170, 255), QColor(255, 170, 0), QColor(255, 170, 255))


def add_striptool_color(color):
    global STRIPTOOL_PREDEFINED_COLORS
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
    A color object randomly selected from the predefined list.
    """
    while True:
        if len(STRIPTOOL_PREDEFINED_COLORS) > 0:
            color_pick = random.choice(STRIPTOOL_PREDEFINED_COLORS)
        else:
            color_pick = random.choice(PREDEFINED_COLORS)
        if not curve_colors_only or (curve_colors_only and color_pick not in (None, QColor("black"), QColor("white"))):
            break

    return color_pick


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

