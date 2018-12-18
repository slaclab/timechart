"""
The Curve Settings Dialog
"""

from pydm import Display
from pydm.widgets.baseplot import BasePlotCurveItem

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import (QFormLayout, QLabel, QComboBox, QSpinBox,
                            QPushButton, QColorDialog, QCheckBox, QGroupBox)
from qtpy.QtGui import QPalette


class CurveSettingsDisplay(Display):
    def __init__(self, main_display, pv_name, parent=None):
        """
        Create all the widgets for the curve appearance settings.

        Parameters
        ----------
        main_display : TimeChartDisplay
            The main display window
        pv_name: str
            The name of the PV the current curve is being plotted for
        parent : QWidget
            The parent widget, if applicable
        """
        super(CurveSettingsDisplay, self).__init__(parent=parent)
        self.main_layout = QFormLayout()
        self.main_display = main_display

        self.chart = self.main_display.chart
        self.pv_name = pv_name
        self.channel_map = self.main_display.channel_map
        self.app = self.main_display.app

        self.curve_original_color = None
        self.curve_color_lbl = QLabel("Curve Color ")
        self.curve_color_btn = QPushButton()
        self.curve_color_btn.setMaximumWidth(20)
        self.curve_color_btn.clicked.connect(
            self.handle_curve_color_button_clicked)

        self.symbol_lbl = QLabel("Symbol")
        self.symbol_cmb = QComboBox()
        self.symbol_size_lbl = QLabel("Symbol Size")
        self.symbol_size_spin = QSpinBox()

        self.line_style_lbl = QLabel("Line Style")
        self.line_style_cmb = QComboBox()
        self.line_width_lbl = QLabel("Line Width")
        self.line_width_spin = QSpinBox()

        self.set_defaults_btn = QPushButton("Reset")
        self.set_defaults_btn.clicked.connect(self.handle_reset_button_clicked)

        self.close_dialog_btn = QPushButton("Close")
        self.close_dialog_btn.clicked.connect(self.handle_close_button_clicked)

        self.setWindowTitle(self.pv_name.split("://")[1])
        self.setFixedSize(QSize(300, 200))
        self.setWindowModality(Qt.ApplicationModal)

        self.setup_ui()

    def ui_filepath(self):
        """
        The path to the UI file created by Qt Designer, if applicable.
        """
        # No UI file is being used
        return None

    def ui_filename(self):
        """
        The name of the UI file created by Qt Designer, if applicable.
        """
        # No UI file is being used
        return None

    def setup_ui(self):
        """
        Initialize the widgets and layouts.
        """
        # Populate the values
        for k, _ in BasePlotCurveItem.symbols.items():
            self.symbol_cmb.addItem(k)
        self.symbol_size_spin.setRange(1, 10)

        for k, _ in BasePlotCurveItem.lines.items():
            self.line_style_cmb.addItem(k)
        self.line_width_spin.setRange(1, 5)

        # Set the widget values to the current settings of the current curve
        self.set_widgets_to_current_curve_settings()

        # Connect to slots to handle signal events
        self.symbol_cmb.currentIndexChanged.connect(
            self.handle_symbol_index_changed)
        self.symbol_size_spin.valueChanged.connect(
            self.handle_symbol_size_changed)

        self.line_style_cmb.currentIndexChanged.connect(
            self.handle_line_style_index_changed)
        self.line_width_spin.valueChanged.connect(
            self.handle_line_width_changed)

        # Add widgets to the form layout
        self.main_layout.setSpacing(10)
        self.main_layout.addRow(self.curve_color_lbl, self.curve_color_btn)
        self.main_layout.addRow(self.symbol_lbl, self.symbol_cmb)
        self.main_layout.addRow(self.symbol_size_lbl, self.symbol_size_spin)
        self.main_layout.addRow(self.line_style_lbl, self.line_style_cmb)
        self.main_layout.addRow(self.line_width_lbl, self.line_width_spin)
        self.main_layout.addRow(self.set_defaults_btn, self.close_dialog_btn)

        # Add the form layout to the main layout of this dialog
        self.setLayout(self.main_layout)

    def set_widgets_to_current_curve_settings(self):
        """
        Make the dialog widgets display the current appearance settings of the current curve.
        """
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            self.curve_color_btn.setStyleSheet(
                "background-color: " + curve.color.name())

            self.set_combo_box(self.symbol_cmb, BasePlotCurveItem.symbols,
                               curve.symbol)
            self.set_combo_box(self.line_style_cmb, BasePlotCurveItem.lines,
                               curve.lineStyle)

            self.symbol_size_spin.setValue(curve.symbolSize)
            self.line_width_spin.setValue(curve.lineWidth)

    def set_combo_box(self, combo_box, reference_dict, curve_setting_value):
        """
        Reverse look up for a dictionary key using a dictionary value, and then set that value to a QComboBox widget.

        Parameters
        ----------
        combo_box : QComboBox
            The combo box to set the current value for
        reference_dict : dict
            The reference dict to find the key from a value to set the combo box
        curve_setting_value : str
            The setting value to look for from the reference_dict
        """
        for k, v in reference_dict.items():
            if curve_setting_value == v:
                combo_box.setCurrentText(k)
                break

    def handle_curve_color_button_clicked(self):
        selected_color = QColorDialog.getColor()
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            self.curve_original_color = curve.color
            curve.color = selected_color
            self.curve_color_btn.setStyleSheet(
                "background-color: " + curve.color.name())

            self.chart.refreshCurve(curve)
            self.channel_map[self.pv_name] = curve

    def handle_symbol_index_changed(self, selected_index):
        """
        Handle the change in the curve's symbol from a combo box.

        Parameters
        ----------
        selected_index : int
            The currently selected index from the symbol combo box
        """
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            curve.symbol = BasePlotCurveItem.symbols[
                self.symbol_cmb.itemText(selected_index)]
            self.chart.refreshCurve(curve)
            self.channel_map[self.pv_name] = curve

    def handle_symbol_size_changed(self, new_size):
        """
        Handle the symbol size value change from the symbol size spinner.

        Parameters
        ----------
        new_size : int
            The new symbol size set by the user.
        """
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            curve.symbolSize = new_size
            self.chart.refreshCurve(curve)
            self.channel_map[self.pv_name] = curve

    def handle_line_width_changed(self, new_width):
        """
        Handle the symbol size value change from the line width spinner.

        Parameters
        ----------
        new_width: int
            The new line width set by the user.
        """
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            curve.lineWidth = new_width
            self.chart.refreshCurve(curve)
            self.channel_map[self.pv_name] = curve

    def handle_line_style_index_changed(self, selected_index):
        """
        Handle the change in the curve's line style from a combo box.

        Parameters
        ----------
        selected_index : int
            The currently selected index from the line style combo box
        """
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            curve.lineStyle = BasePlotCurveItem.lines[
                self.line_style_cmb.itemText(selected_index)]
            self.chart.refreshCurve(curve)
            self.channel_map[self.pv_name] = curve

    def handle_reset_button_clicked(self):
        """
        Handle the click of the Reset button. This will set all the dialog widgets to the default curve appearance
        settings.
        """
        curve = self.chart.findCurve(self.pv_name)
        if curve:
            if self.curve_original_color:
                curve.color = self.curve_original_color
                self.curve_color_btn.setStyleSheet(
                    "background-color: " + curve.color.name())

            self.symbol_cmb.setCurrentIndex(0)
            self.symbol_size_spin.setValue(10)

            self.line_style_cmb.setCurrentIndex(1)
            self.line_width_spin.setValue(1)

    def closeEvent(self, event):
        self.handle_close_button_clicked()

    def handle_close_button_clicked(self):
        """
        Close the dialog when the Close button is clicked.
        """
        self.close()

        curve = self.chart.findCurve(self.pv_name)
        if curve:
            # Update the widget checkbox text to the current curve color
            widget = self.main_display.findChild(QGroupBox, self.pv_name + "_grb")
            chb = widget.findChild(QCheckBox, self.pv_name + "_chb")
            lbl = widget.findChild(QLabel, self.pv_name + "_lbl")
            widget = [chb, lbl]
            for w in widget:
                palette = w.palette()
                palette.setColor(QPalette.Active, QPalette.WindowText,
                                 curve.color)
                w.setPalette(palette)
