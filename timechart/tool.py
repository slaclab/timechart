from pydm.tools import ExternalTool
from typing import List, Optional
import subprocess
import threading

from qtpy import QtWidgets


def run_timechart(*pvs: str) -> subprocess.Popen:
    """
    Run timechart in a subprocess with the provided PVs.

    Parameters
    ----------
    *pvs : str
        The PV names to plot at startup.

    Returns
    -------
    code : int
        The return value of the subprocess.
    """
    if pvs:
        pv_args = ["--pvs"] + list(pvs)
    else:
        pv_args = []

    return subprocess.call(["timechart"] + pv_args)


_background_threads = []


def run_timechart_in_thread(*args, **kwargs):
    """
    Run timechart in a background thread subprocess.

    See :func:`run_timechart` for argument details.
    """

    def thread():
        run_timechart(*args, **kwargs)

    th = threading.Thread(target=thread, daemon=True)
    th.start()


class PydmTimeChartTool(ExternalTool):
    def __init__(self):
        super().__init__(
            icon=None,
            name="timechart",
            group="",
            author="SLAC National Accelerator Laboratory",
            use_with_widgets=True,
            use_without_widget=True,
        )

    def call(self, channels: Optional[List], sender: QtWidgets.QWidget):
        """
        This method is invoked when the tool is selected at the menu.

        Parameters
        ----------
        channels : list or None
            The list of channels in use at the widget.
        sender : PyDMWidget
            The PyDMWidget or Main Window that triggered the action.
        """
        pv_names = [
            ch.address for ch in channels or []
            if ch is not None and ch.address
        ]
        run_timechart_in_thread(*pv_names)

    def to_json(self):
        """
        Serialize the information at this tool in order to make it possible
        to be added to another PyDM Application without user interference.

        Returns
        -------
        str
        """
        return ""

    def from_json(self, content):
        """
        Recreate the tool based on the serialized information sent as parameter.

        Parameters
        ----------
        content : str
        """

    def get_info(self):
        """
        Retrieve basic information about the External Tool in a format
        that is parsed and used at the About screen.

        Returns
        -------
        dict
            Dictionary containing at least `author`, `file`, `group` and
            `name` of the External Tool.
        """

        return {
            "author": self.author,
            "file": "",
            "group": self.group,
            "name": self.name,
        }

    def is_compatible_with(self, widget: QtWidgets.QWidget):
        """
        Verify if the ExternalTool is compatible with the given widget.

        Parameters
        ----------
        widget : QWidget
            The widget for which the ExternalTool is being assembled.

        Returns
        -------
        bool
            True if this ExternalTool is compatible with the widget, False
            otherwise.
        """
        return True
