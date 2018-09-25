import random

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QMessageBox

PREDEFINED_COLORS = (Qt.red, Qt.green,  Qt.darkRed,  Qt.blue, Qt.darkGreen,  Qt.cyan,  Qt.darkBlue,  Qt.darkCyan,
                     Qt.magenta,  Qt.darkMagenta)


def random_color():
    """
    Return a QColor object from a predefined list.

    Returns
    -------
    A color object randomly selected from the predefined list.
    """
    return QColor(random.choice(PREDEFINED_COLORS))


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

