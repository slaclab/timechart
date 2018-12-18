"""
The Dialog to Export Data from a Chart
"""

from functools import partial

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import (QFormLayout, QCheckBox, QLabel, QLineEdit,
                            QPushButton, QHBoxLayout, QFontDialog)
from pydm import Display
from pydm.utilities.iconfont import IconFont

from .defaults import X_AXIS_LABEL_SEPARATOR


class AxisSettingsDisplay(Display):
    def __init__(self, main_display, parent=None):
        super(AxisSettingsDisplay, self).__init__(parent=parent)
        self.main_layout = QFormLayout()
        self.main_display = main_display

        self.chart = self.main_display.chart

        self.x_axis_lbl = QLabel("x-axis Label")
        self.x_axis_label_line_edt = QLineEdit()
        current_x_label = self.chart.labels["bottom"]
        if current_x_label:
            current_x_label = current_x_label[
                              current_x_label.find(X_AXIS_LABEL_SEPARATOR) +
                              len(X_AXIS_LABEL_SEPARATOR):]
            self.x_axis_label_line_edt.setText(current_x_label)
        self.x_axis_label_line_edt.textChanged.connect(
            partial(self.handle_axis_label_change, "bottom"))

        self.x_axis_font_btn = QPushButton()
        self.x_axis_font_btn.setMaximumHeight(32)
        self.x_axis_font_btn.setMaximumWidth(32)
        self.x_axis_font_btn.setIcon(IconFont().icon("font"))
        self.x_axis_font_btn.clicked.connect(
            partial(self.handle_font_change, "bottom")
        )

        self.x_axis_unit_lbl = QLabel("x-axis Unit")
        self.x_axis_unit_edt = QLineEdit()
        self.x_axis_unit_edt.setMaximumWidth(150)
        self.x_axis_unit_edt.setText(self.chart.units["bottom"])
        self.x_axis_unit_edt.textChanged.connect(
            partial(self.handle_axis_label_change, "bottom", is_unit=True))

        self.y_axis_lbl = QLabel("y-axis Label")
        self.y_axis_label_line_edt = QLineEdit()
        self.y_axis_label_line_edt.setText(self.chart.labels["left"])
        self.y_axis_label_line_edt.textChanged.connect(
            partial(self.handle_axis_label_change, "left"))

        self.y_axis_font_btn = QPushButton()
        self.y_axis_font_btn.setMaximumHeight(32)
        self.y_axis_font_btn.setMaximumWidth(32)
        self.y_axis_font_btn.setIcon(IconFont().icon("font"))
        self.y_axis_font_btn.clicked.connect(
            partial(self.handle_font_change, "left")
        )


        self.y_axis_unit_lbl = QLabel("y-axis Unit")
        self.y_axis_unit_edt = QLineEdit()
        self.y_axis_unit_edt.setMaximumWidth(150)
        self.y_axis_unit_edt.setText(self.chart.units["left"])
        self.y_axis_unit_edt.textChanged.connect(
            partial(self.handle_axis_label_change, "left", is_unit=True))

        self.right_y_axis_label_line_edt = QLineEdit()

        self.display_right_y_axis_chk = QCheckBox("Display the right y-axis")
        self.display_right_y_axis_chk.setChecked(self.chart.getShowRightAxis())
        self.display_right_y_axis_chk.clicked.connect(
            self.handle_right_y_axis_checkbox_changed)
        self.display_right_y_axis_chk.setChecked(self.chart.getShowRightAxis())

        self.right_y_axis_lbl = None
        self.right_y_axis_unit_edt = None
        self.right_y_axis_unit_lbl = None
        self.right_y_axis_unit_edt = None

        self.close_dialog_btn = QPushButton("Close")
        self.close_dialog_btn.clicked.connect(self.handle_close_button_clicked)

        self.setWindowTitle("Axis Settings")
        self.setMinimumSize(500, 300)
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
        x_axis_layout = QHBoxLayout()
        x_axis_layout.addWidget(self.x_axis_label_line_edt)
        x_axis_layout.addWidget(self.x_axis_font_btn)

        y_axis_layout = QHBoxLayout()
        y_axis_layout.addWidget(self.y_axis_label_line_edt)
        y_axis_layout.addWidget(self.y_axis_font_btn)

        # Add widgets to the form layout
        self.main_layout.setSpacing(10)
        self.main_layout.addRow(self.x_axis_lbl, x_axis_layout)
        self.main_layout.addRow(self.x_axis_unit_lbl, self.x_axis_unit_edt)
        self.main_layout.addRow(self.y_axis_lbl, y_axis_layout)
        self.main_layout.addRow(self.y_axis_unit_lbl, self.y_axis_unit_edt)
        self.main_layout.addRow(self.display_right_y_axis_chk, None)
        self.main_layout.addRow(None, self.close_dialog_btn)

        self.display_right_y_axis_chk.setChecked(self.chart.getShowRightAxis())
        if self.chart.getShowRightAxis():
            self.display_right_y_axis_chk.clicked.emit(
                self.chart.getShowRightAxis())

        self.setLayout(self.main_layout)

    def handle_right_y_axis_checkbox_changed(self, is_checked):
        self.chart.setShowRightAxis(is_checked)

        if is_checked:
            right_label = self.chart.labels["right"]
            if not right_label:
                right_label = self.y_axis_label_line_edt.text()
            right_unit = self.chart.units["right"]
            if not right_unit:
                right_unit = self.y_axis_unit_edt.text()

            self.right_y_axis_font_btn = QPushButton()
            self.right_y_axis_font_btn.setMaximumHeight(32)
            self.right_y_axis_font_btn.setMaximumWidth(32)
            self.right_y_axis_font_btn.setIcon(IconFont().icon("font"))
            self.right_y_axis_font_btn.clicked.connect(
                partial(self.handle_font_change, "right")
            )

            self.right_y_axis_lbl = QLabel("Right y-axis Label")
            self.right_y_axis_label_line_edt = QLineEdit()
            self.right_y_axis_label_line_edt.textChanged.connect(
                partial(self.handle_axis_label_change, "right"))

            self.right_y_axis_unit_lbl = QLabel("Right y-axis Unit")
            self.right_y_axis_unit_edt = QLineEdit()
            self.right_y_axis_unit_edt.setMaximumWidth(150)
            self.right_y_axis_unit_edt.textChanged.connect(
                partial(self.handle_axis_label_change, "right",
                        is_unit=True))

            self.right_y_axis_label_line_edt.setText(right_label)
            self.right_y_axis_unit_edt.setText(right_unit)

            right_y_axis_layout = QHBoxLayout()
            right_y_axis_layout.addWidget(self.right_y_axis_label_line_edt)
            right_y_axis_layout.addWidget(self.right_y_axis_font_btn)

            self.main_layout.insertRow(self.main_layout.rowCount() - 1,
                                       self.right_y_axis_lbl,
                                       right_y_axis_layout)
            self.main_layout.insertRow(self.main_layout.rowCount() - 1,
                                       self.right_y_axis_unit_lbl,
                                       self.right_y_axis_unit_edt)
        else:
            self.chart.showAxis("right", show=False)
            self.right_y_axis_lbl.deleteLater()
            self.right_y_axis_label_line_edt.deleteLater()
            self.right_y_axis_unit_lbl.deleteLater()
            self.right_y_axis_unit_edt.deleteLater()
            self.right_y_axis_font_btn.deleteLater()

    def handle_axis_label_change(self, axis_position, new_label, is_unit=False):
        if is_unit:
            self.chart.setLabel(axis_position, units=new_label)
            self.chart.units[axis_position] = new_label
        else:
            if axis_position == "bottom":
                current_label = self.chart.getBottomAxisLabel()
                if X_AXIS_LABEL_SEPARATOR in current_label:
                    current_label = current_label[:current_label.find(
                        X_AXIS_LABEL_SEPARATOR) - len(X_AXIS_LABEL_SEPARATOR)]
                new_label = current_label + X_AXIS_LABEL_SEPARATOR + new_label
            self.chart.setLabel(axis_position, text=new_label)
            self.chart.labels[axis_position] = new_label
        return

    def change_axis_font(self, axis, font):
        axis.setTickFont(font)
        axis.label.setFont(font)

    def handle_font_change(self, axis_position):
        axis = self.chart.getAxis(axis_position)
        label = axis.label
        initial = axis.tickFont

        dialog = QFontDialog(self)
        if initial:
            dialog.setCurrentFont(initial)
        dialog.setOption(QFontDialog.DontUseNativeDialog, True)
        dialog.fontSelected.connect(partial(self.change_axis_font, axis))
        dialog.open()

    def closeEvent(self, event):
        self.handle_close_button_clicked()

    def handle_close_button_clicked(self):
        """
        Close the dialog when the Close button is clicked.
        """
        self.close()
