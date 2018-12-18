"""
StripTool Configuration Data File Import Strategy
"""

from collections import OrderedDict
import re

from qtpy.QtGui import QColor
from qtpy.QtCore import Qt

from timechart import __version__ as ver

from .timechart_config_importer import TimeChartConfigImporter
from ...utilities.utils import add_striptool_color
from timechart.displays.defaults import DEFAULT_CHART_TITLE, ASYNC_DATA_SAMPLING


def _convert_to_bool(key, chart_settings, value):
    chart_settings[key] = True if int(value) > 0 else False


def _convert_to_int(key, chart_settings, value):
    chart_settings[key] = int(value)


def _convert_to_float(key, chart_settings, value):
    chart_settings[key] = float(value)


def _convert_to_hz(key, chart_settings, time_per_second):
    chart_settings[key] = 1.0 / float(time_per_second)


def _adjust_color_value(color_value):
    try:
        color_value = color_value.rstrip().split(" ")
        color = QColor(int(color_value[0]) // 257, int(color_value[1]) // 257, int(color_value[2]) // 257)

        return color
    except IndexError as error:
        raise error


def _convert_to_qcolor(key, chart_settings, color_value):
    chart_settings[key] = _adjust_color_value(color_value)


def _convert_to_time_span(chart_settings, time_span_seconds):
    time_span_seconds = int(time_span_seconds)
    if time_span_seconds:
        chart_settings["limit_time_span"] = True
        minutes, seconds = divmod(time_span_seconds, 60)
        hours, minutes = divmod(minutes, 60)

        chart_settings["time_span_limit_hours"] = hours
        chart_settings["time_span_limit_minutes"] = minutes
        chart_settings["time_span_limit_seconds"] = seconds


global LINE_WIDTH
LINE_WIDTH = 1


def _add_to_curves(key, value, chart_pvs, index_to_pv_names):
    """
    Form a list of PVs from parsing the StripTool configuration file.
    Then, determine the specific values for each PV to assign to the TimeChart configuration data structure.

    Parameters
    ----------
    key : str
        A key from the StripTool config file
    value : str
        A value paired with a key from the StripTool config file
    chart_pvs : OrderedDict
        A dictionary of PVs, and for each PV, there's a nested dict to hold the PV's specific attribute values
    index_to_pv_names : OrderedDict
        A map between the StripTool's label for each PV, and the PV name.
    """
    key_components = key.split('.')
    key_specific_item = key_components[-1]
    key_index = int(key_components[-2])

    if "Name" in key:
        value = "ca://" + value
        chart_pvs[value] = OrderedDict()

        global LINE_WIDTH
        chart_pvs[value]["line_width"] = LINE_WIDTH

        chart_pvs[value]["y_channel"] = value
        chart_pvs[value]["line_style"] = Qt.SolidLine
        chart_pvs[value]["symbol"] = None
        chart_pvs[value]["symbol_size"] = 1

        index_to_pv_names[key_index] = value
    else:
        pv_name = index_to_pv_names[key_index]
        converted_content = StripToolConfigImporter.CONVERSION_TABLE[key_specific_item]

        if isinstance(converted_content, tuple):
            if converted_content[0]:
                converted_content[1](converted_content[0], chart_pvs[pv_name], value)
            else:
                converted_content[1](chart_pvs[pv_name], value)
        else:
            chart_pvs[pv_name][converted_content] = value


def _customize_colors(value):
    """
    Add the StripTool-defined colors to TimeChart's random color collections.

    Parameters
    ----------
    value : QColor
        A StripTool-defined color, as specified in the StripTool config file.
    """
    add_striptool_color(_adjust_color_value(value))


def _convert_to_line_width(_, __, line_width_value):
    """
    Since StripTool defines the same line width for all curves while TimeChart lets each curve have its own line width,
    here we must import the global StripTool line width, save it to a global variable, and then, whenever it's time
    to provide the line width for a curve, retrieve the global line width variable to assign to that curve.

    Parameters
    ----------
    line_width_value : str
        The line width as set by the StripTool config file.
    """
    global LINE_WIDTH
    LINE_WIDTH = int(line_width_value)


class StripToolConfigImporter(TimeChartConfigImporter):
    """
    The strategy to import a StripTool configuration data file.
    """
    CONVERSION_TABLE = {
        "Units": "unit",
        "Comment": "comment",
        "Min": ("x_min", _convert_to_float),
        "Max": ("x_max", _convert_to_float),
        "Scale": ("scale", _convert_to_int),
        "PlotStatus": ("is_visible", _convert_to_bool),
        "Precision": ("precision", _convert_to_int),
        "Strip.Time.NumSamples": "buffer_size",
        "Strip.Time.SampleInterval": ("update_interval_hz", _convert_to_hz),
        "Strip.Time.Timespan": (None, _convert_to_time_span),
        "Strip.Time.RefreshInterval": ("redraw_rate", _convert_to_hz),
        "Strip.Color.Background": ("background_color", _convert_to_qcolor),
        "Strip.Color.Grid": ("axis_color", _convert_to_qcolor),
        "Strip.Option.GridXon": ("show_x_grid", _convert_to_bool),
        "Strip.Option.GridYon": ("show_y_grid", _convert_to_bool),
        "Strip.Option.GraphLineWidth": ("line_width", _convert_to_line_width)
    }

    def __init__(self, pydm_main_display):
        """
        Parameters
        ----------
        pydm_main_display : PyDMDisplay
            The Main Display Window.
        """
        super(StripToolConfigImporter, self).__init__(pydm_main_display)

    def import_to_dict(self, settings_file):
        """
        Parse the StripTool config file.

        Parameters
        ----------
        settings_file : TextIOWrapper
            The file object to parse

        Returns
        -------
            The file data as a dictionary
        """
        lines = [line.rstrip('\n') for line in settings_file.readlines()]
        stp_data = self._read_file_into_dict(lines)
        return stp_data

    def convert_to_timechart_setting(self, stp_data):
        """
        Convert StripTool settings into TimeChart settings

        Parameters
        ----------
        stp_data : dict
            The StripTool data to convert.

        Returns
        -------
            The equivalent TimeChart settings.

        """
        timechart_settings = OrderedDict()
        timechart_settings["__version__"] = ver

        timechart_settings["pvs"] = OrderedDict()

        timechart_settings["chart_settings"] = OrderedDict()
        timechart_settings["chart_settings"]["title"] = DEFAULT_CHART_TITLE
        timechart_settings["chart_settings"]["x_axis_label"] = None
        timechart_settings["chart_settings"]["x_axis_unit"] = None
        timechart_settings["chart_settings"]["left_y_axis_label"] = None
        timechart_settings["chart_settings"]["left_y_axis_unit"] = None
        timechart_settings["chart_settings"]["right_y_axis_label"] = None
        timechart_settings["chart_settings"]["right_y_axis_unit"] = None
        timechart_settings["chart_settings"]["data_sampling_mode"] = ASYNC_DATA_SAMPLING
        timechart_settings["chart_settings"]["show_legend"] = False
        timechart_settings["chart_settings"]["grid_alpha"] = 5

        index_to_pv_name = OrderedDict()
        for k, v in stp_data.items():
            converted_content = StripToolConfigImporter.CONVERSION_TABLE.get(k, None)

            if "Strip.Curve" in k:
                _add_to_curves(k, v, timechart_settings["pvs"], index_to_pv_name)
            elif "Strip.Color" in k:
                _customize_colors(v)

            if isinstance(converted_content, tuple):
                if converted_content[0]:
                    converted_content[1](converted_content[0], timechart_settings["chart_settings"], v)
                else:
                    converted_content[1](timechart_settings["chart_settings"], v)
            elif converted_content:
                timechart_settings["chart_settings"][converted_content] = v

        return timechart_settings

    def _read_file_into_dict(self, file_contents):
        """
        Parse a file's contents into a dictionary for subsequent filtering.
        For each line, expect two strings, separated by a space. The first string becomes a dictionary entry's key,
        and the next one is the dictionary entry's value.

        Parameters
        ----------
        file_contents : list
            A list of strings, each of which is a line from a text file

        Returns
        -------
            A dictionary with the keys and values parsed from the file contents.
        """
        settings_modules = OrderedDict()
        for line in file_contents:
            tokens = re.sub(' +', ' ', line.lstrip())
            tokens = tokens.split(' ', 1)
            try:
                settings_modules[tokens[0]] = tokens[1]
            except IndexError:
                settings_modules[tokens[0]] = None
        return settings_modules
