# TimeChart Configuration Data File Import Strategy

import json
from qtpy.QtGui import QColor

from ...displays.defaults import ASYNC_DATA_SAMPLING, SYNC_DATA_SAMPLING
from .settings_import_strategy import SettingsImportStrategy, SettingsImportException
from ...utilities.utils import random_color

import logging
logger = logging.getLogger(__name__)


class TimeChartImportStrategy(SettingsImportStrategy):
    def __init__(self, pydm_main_dislay):
        """

        Parameters
        ----------
        pydm_main_dislay : PyDMDisplay
            The Main Window object.
        """
        super(TimeChartImportStrategy, self).__init__(pydm_main_dislay)

    def import_file(self, filename):
        """
        Import a TimeChart configuration file (in the JSON format).

        Parameters
        ----------
        filename : str
            The path to the TimeChart configuration file.

        Raises SettingsImportException
        """
        with open(filename, 'r') as settings_file:
            try:
                settings = json.load(settings_file)
                SettingsImportStrategy.apply_settings(settings, self.main_display)
            except Exception as error:
                raise SettingsImportException("Encountered exception: '{0}'".format(error))

    @classmethod
    def apply_settings(cls, settings, main_display):
        """
        Apply the imported settings to the TimeChart's Main Display.

        Parameters
        ----------
        settings : OrderedDict
            A dictionary of all the imported settings

        main_display : PyDMDisplay
            The TimeChart's Main Display
        """
        chart = main_display.chart

        pv_settings = settings["pvs"]
        for k, v in pv_settings.items():
            color_value = v.get("color", None)
            if color_value:
                color = QColor(color_value)
            else:
                color = random_color(curve_colors_only=True)

            is_visible = v.get("is_visible", True)
            main_display.add_y_channel(pv_name=v["y_channel"],
                                       curve_name=k,
                                       color=color,
                                       line_style=v["line_style"],
                                       line_width=v["line_width"],
                                       symbol=v["symbol"],
                                       symbol_size=v["symbol_size"],
                                       is_visible=is_visible)
        chart_settings = settings["chart_settings"]

        if len(chart_settings):
            main_display.chart_title_line_edt.textChanged.emit(
                chart_settings["title"])

            chart.setLabel("bottom", text=chart_settings["x_axis_label"])
            chart.labels["bottom"] = chart_settings["x_axis_label"]

            chart.setLabel("bottom", unit=chart_settings["x_axis_unit"])

            chart.setLabel("left", text=chart_settings["left_y_axis_label"])
            chart.setLabel("left", unit=chart_settings["left_y_axis_unit"])

            if chart_settings.get("show_right_y_axis", False):
                chart.setShowRightAxis(True)
                chart.setLabel("right", text=chart_settings["right_y_axis_label"])
                chart.setLabel("right", unit=chart_settings["right_y_axis_unit"])

            main_display.chart_redraw_rate_spin.setValue(
                chart_settings["redraw_rate"])
            main_display.handle_redraw_rate_changed()

            data_sampling_mode = chart_settings["data_sampling_mode"]
            main_display.chart_sync_mode_sync_radio.setChecked(
                data_sampling_mode == SYNC_DATA_SAMPLING)
            main_display.chart_sync_mode_async_radio.setChecked(
                data_sampling_mode == ASYNC_DATA_SAMPLING)
            main_display.chart_sync_mode_async_radio.toggled.emit(
                data_sampling_mode == ASYNC_DATA_SAMPLING)

            main_display.chart_data_async_sampling_rate_spin.setValue(
                chart_settings["update_interval_hz"])
            main_display.handle_data_sampling_rate_changed()

            time_span_limit_hours = int(chart_settings["time_span_limit_hours"])
            time_span_limit_minutes = int(
                chart_settings["time_span_limit_minutes"])
            time_span_limit_seconds = int(
                chart_settings["time_span_limit_seconds"])

            main_display.chart_ring_buffer_size_edt.setText(
                str(chart_settings["buffer_size"]))
            main_display.chart_ring_buffer_size_edt.textChanged.emit(
                str(chart_settings["buffer_size"]))

            if time_span_limit_hours != 0 or time_span_limit_minutes != 0 or time_span_limit_seconds != 0:
                main_display.chart_limit_time_span_hours_spin_box.setValue(
                    time_span_limit_hours)
                main_display.chart_limit_time_span_hours_spin_box.valueChanged.emit(
                    time_span_limit_hours)

                main_display.chart_limit_time_span_minutes_spin_box.setValue(
                    time_span_limit_minutes)
                main_display.chart_limit_time_span_minutes_spin_box.valueChanged.emit(
                    time_span_limit_minutes)

                main_display.chart_limit_time_span_seconds_spin_box.setValue(
                    time_span_limit_seconds)
                main_display.chart_limit_time_span_seconds_spin_box.valueChanged.emit(
                    time_span_limit_seconds)

                main_display.chart_limit_time_span_chk.setChecked(
                    chart_settings["limit_time_span"])
                main_display.chart_limit_time_span_chk.clicked.emit(
                    chart_settings["limit_time_span"])

                main_display.chart_limit_time_span_activate_btn.clicked.emit()

            main_display.show_legend_chk.setChecked(
                chart_settings["show_legend"])
            main_display.show_legend_chk.clicked.emit(
                chart_settings["show_legend"])

            background_color = QColor(chart_settings["background_color"])
            main_display.chart.setBackgroundColor(background_color)
            main_display.background_color_btn.setStyleSheet(
                "background-color: " + background_color.name())

            axis_color = QColor(chart_settings["axis_color"])
            main_display.chart.setAxisColor(axis_color)
            main_display.axis_color_btn.setStyleSheet(
                "background-color: " + axis_color.name())

            main_display.show_x_grid_chk.setChecked(
                chart_settings["show_x_grid"])
            main_display.show_x_grid_chk.clicked.emit(
                chart_settings["show_x_grid"])

            main_display.show_y_grid_chk.setChecked(
                chart_settings["show_y_grid"])
            main_display.show_y_grid_chk.clicked.emit(
                chart_settings["show_y_grid"])

            main_display.grid_opacity_slr.valueChanged.emit(
                chart_settings["grid_alpha"])
            main_display.grid_opacity_slr.setValue(
                chart_settings["grid_alpha"])

            main_display.app.establish_widget_connections(
                main_display)
