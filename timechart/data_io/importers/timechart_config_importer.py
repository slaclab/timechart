"""
The settings importer to process TimeChart configuration data
"""

from qtpy.QtGui import QColor

from ...displays.defaults import ASYNC_DATA_SAMPLING, SYNC_DATA_SAMPLING
from ...utilities.utils import random_color


class TimeChartConfigImporter(object):
    def __init__(self, pydm_main_dislay):
        self.main_display = pydm_main_dislay
        self.chart = self.main_display.chart if self.main_display else None

    def _set_chart_labels(self, chart_labels):
        """
        Set the text and unit for individual labels from a chart label collection.

        Parameters
        ----------
        chart_labels : dict
            A dictionary holding the label position as the key, and a tuple of (text, unit) as the value.
            Either text or unit, or both, will be set as long as each value is not None.
        """
        for label_position, label_data in chart_labels.items():
            text = label_data[0]
            unit = label_data[1]
            if text:
                self.chart.setLabel(label_position, text=text)
            if unit:
                self.chart.setLabel(label_position, unit=unit)

    def _set_chart_values(self, chart_values):
        """
        Set the value for each individual UI widget.
        Parameters
        ----------
        chart_values : dict
            A dictionary containing widgets as the keys, and the widget values as the values.
        """
        for widget, widget_value in chart_values.items():
            widget.setValue(widget_value)

        self.main_display.handle_data_sampling_rate_changed()
        self.main_display.handle_redraw_rate_changed()
        if self.main_display.chart_limit_time_span_chk.isChecked():
            self.main_display.chart_limit_time_span_chk.clicked.emit(True)
            self.main_display.handle_time_span_changed()
            self.main_display.chart_limit_time_span_activate_btn.clicked.emit()

    def _set_chart_checkboxes(self, checked_data):
        """
        Set the "checked" status of individual checkboxes.

        Parameters
        ----------
        checked_data : dict
            A dictionary with checkboxes as the keys, and their corresponding checked/unchecked statuses as the values.
        """
        for widget, widget_value in checked_data.items():
            widget.setChecked(widget_value)

    def _set_chart_colors(self, color_data):
        """
        Paint a color to a chart's component (axis or background) while also painting the background of the button
        widget setting the corresponding component.

        Parameters
        ----------
        color_data : dict
            A dictionary with widgets as the keys, and the color data as the values.
            The color data contains the color to paint, and the functor to apply the color change to a chart's
            component.
        """
        for widget, data in color_data.items():
            color = QColor(data[0])
            set_color_fn = data[1]

            set_color_fn(color)
            widget.setStyleSheet("background-color: " + color.name())

    def apply_settings(self, settings):
        """
        Apply the imported settings to the TimeChart's Main Display.

        Parameters
        ----------
        settings : OrderedDict
            A dictionary of all the imported settings

        self.main_display : PyDMDisplay
            The TimeChart's Main Display
        """        
        pv_settings = settings["pvs"]
        for k, v in pv_settings.items():
            color_value = v.get("color", None)
            color = QColor(color_value) if color_value else random_color(curve_colors_only=True)
            self.main_display.add_y_channel(pv_name=v["y_channel"],
                                            curve_name=k,
                                            color=color,
                                            line_style=v["line_style"],
                                            line_width=v["line_width"],
                                            symbol=v["symbol"],
                                            symbol_size=v["symbol_size"],
                                            is_visible=v.get("is_visible", True))

        chart_settings = settings["chart_settings"]
        if len(chart_settings):
            self.main_display.chart_title_line_edt.textChanged.emit(
                chart_settings["title"])

            chart_labels = {
                "bottom": (chart_settings["x_axis_label"], chart_settings["x_axis_unit"]),
            }
            if chart_settings.get("show_right_y_axis", False):
                chart_labels["right"] = (chart_settings["right_axis_label"], chart_settings["right_axis_unit"]),
            if chart_settings.get("left_axis_label", None):
                chart_labels["left"] = (chart_settings["left_axis_label"], chart_settings["left_axis_unit"]),
            self._set_chart_labels(chart_labels)

            data_sampling_mode = chart_settings["data_sampling_mode"]
            chart_checked_data = {
                self.main_display.chart_sync_mode_sync_radio: data_sampling_mode == SYNC_DATA_SAMPLING,
                self.main_display.chart_sync_mode_async_radio: data_sampling_mode == ASYNC_DATA_SAMPLING,
                self.main_display.chart_limit_time_span_chk: chart_settings["limit_time_span"],
                self.main_display.show_legend_chk: chart_settings["show_legend"],
                self.main_display.show_x_grid_chk: chart_settings["show_x_grid"],
                self.main_display.show_y_grid_chk: chart_settings["show_y_grid"]
            }
            self._set_chart_checkboxes(chart_checked_data)
            self.main_display.show_legend_chk.clicked.emit(chart_settings["show_legend"])
            self.main_display.show_x_grid_chk.clicked.emit(chart_settings["show_x_grid"])
            self.main_display.show_y_grid_chk.clicked.emit(chart_settings["show_y_grid"])

            chart_values = {
                self.main_display.chart_redraw_rate_spin: chart_settings["redraw_rate"],
                self.main_display.chart_data_async_sampling_rate_spin: chart_settings["update_interval_hz"],
                self.main_display.grid_opacity_slr: chart_settings["grid_alpha"],
            }

            time_span_limit_hours = int(chart_settings["time_span_limit_hours"])
            time_span_limit_minutes = int(chart_settings["time_span_limit_minutes"])
            time_span_limit_seconds = int(chart_settings["time_span_limit_seconds"])
            timespan_values = {
                self.main_display.chart_limit_time_span_hours_spin_box: time_span_limit_hours,
                self.main_display.chart_limit_time_span_minutes_spin_box: time_span_limit_minutes,
                self.main_display.chart_limit_time_span_seconds_spin_box: time_span_limit_seconds,
            }
            chart_values.update(timespan_values)
            self._set_chart_values(chart_values)

            self.main_display.chart_ring_buffer_size_edt.setText(str(chart_settings["buffer_size"]))
            self.main_display.handle_buffer_size_changed()

            color_data = {
                self.main_display.background_color_btn: (chart_settings["background_color"],
                                                         self.main_display.chart.setBackgroundColor),
                self.main_display.axis_color_btn: (chart_settings["axis_color"],
                                                   self.main_display.chart.setAxisColor)
            }
            self._set_chart_colors(color_data)
