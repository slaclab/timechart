# The Dialog to Export Data from a Chart

from functools import partial

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import QFormLayout, QCheckBox, QFileDialog, QLabel, QLineEdit, QPushButton
from pydm import Display

X_AXIS_LABEL_SEPARATOR = " -- "


class AxisSettingsDisplay(Display):
    def __init__(self, main_display, parent=None):
        super(AxisSettingsDisplay, self).__init__(parent=parent)
        self.main_layout = QFormLayout()
        self.main_display = main_display

        self.chart = self.main_display.chart
        self.app = self.main_display.app

        self.x_axis_lbl = QLabel("x-axis Label")
        self.x_axis_label_line_edt = QLineEdit()
        current_x_label = self.chart.labels["bottom"]
        if current_x_label:
            current_x_label = current_x_label[current_x_label.find(X_AXIS_LABEL_SEPARATOR) +
                                              len(X_AXIS_LABEL_SEPARATOR):]
            self.x_axis_label_line_edt.setText(current_x_label)
        self.x_axis_label_line_edt.textChanged.connect(partial(self.handle_axis_label_change, "bottom"))

        self.x_axis_unit_lbl = QLabel("x-axis Unit")
        self.x_axis_unit_edt = QLineEdit()
        self.x_axis_unit_edt.setText(self.chart.units["bottom"])
        self.x_axis_unit_edt.textChanged.connect(partial(self.handle_axis_label_change, "bottom", is_unit=True))

        self.y_axis_lbl = QLabel("y-axis Label")
        self.y_axis_label_line_edt = QLineEdit()
        self.y_axis_label_line_edt.setText(self.chart.labels["left"])
        self.y_axis_label_line_edt.textChanged.connect(partial(self.handle_axis_label_change, "left"))

        self.y_axis_unit_lbl = QLabel("y-axis Unit")
        self.y_axis_unit_edt = QLineEdit()
        self.y_axis_unit_edt.setText(self.chart.units["left"])
        self.y_axis_unit_edt.textChanged.connect(partial(self.handle_axis_label_change, "left", is_unit=True))

        self.right_y_axis_label_line_edt = QLineEdit()
        self.right_y_axis_lbl = QLabel("Right y-axis Label")

        self.display_right_y_axis_chk = QCheckBox("Display the right y-axis")
        self.display_right_y_axis_chk.setChecked(self.chart.getShowRightAxis())
        self.display_right_y_axis_chk.clicked.connect(self.handle_right_y_axis_checkbox_changed)
        self.display_right_y_axis_chk.setChecked(self.chart.getShowRightAxis())

        self.right_y_axis_lbl = None
        self.right_y_axis_unit_edt = None
        self.right_y_axis_unit_lbl = None
        self.right_y_axis_unit_edt = None

        self.close_dialog_btn = QPushButton("Close")
        self.close_dialog_btn.clicked.connect(self.handle_close_button_clicked)

        self.setWindowTitle("Axis Settings")
        self.setFixedSize(QSize(300, 250))
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
        # Add widgets to the form layout
        self.main_layout.setSpacing(10)
        self.main_layout.addRow(self.x_axis_lbl, self.x_axis_label_line_edt)
        self.main_layout.addRow(self.x_axis_unit_lbl, self.x_axis_unit_edt)
        self.main_layout.addRow(self.y_axis_lbl, self.y_axis_label_line_edt)
        self.main_layout.addRow(self.y_axis_unit_lbl, self.y_axis_unit_edt)
        self.main_layout.addRow(self.display_right_y_axis_chk, None)
        self.main_layout.addRow(None, self.close_dialog_btn)

        self.setLayout(self.main_layout)

        if self.chart.getShowRightAxis():
            self.display_right_y_axis_chk.clicked.emit(True)

    def handle_right_y_axis_checkbox_changed(self, is_checked):
        self.chart.setShowRightAxis(is_checked)

        # Remove the Close button first
        self.main_layout.removeRow(self.main_layout.rowCount() - 1)

        if is_checked:
            right_label = self.chart.labels["right"]
            if not right_label:
                right_label = self.y_axis_label_line_edt.text()
            right_unit = self.chart.units["right"]
            if not right_unit:
                right_unit = self.y_axis_unit_edt.text()

            self.right_y_axis_label_line_edt.textChanged.connect(partial(self.handle_axis_label_change, "right"))

            self.right_y_axis_unit_lbl = QLabel(text="Right y-axis Unit")
            self.right_y_axis_unit_edt = QLineEdit()
            self.right_y_axis_unit_edt.textChanged.connect(
                partial(self.handle_axis_label_change, "right", is_unit=True))

            self.right_y_axis_label_line_edt.setText(right_label)
            self.right_y_axis_unit_edt.setText(right_unit)

            self.main_layout.addRow(self.right_y_axis_lbl, self.right_y_axis_label_line_edt)
            self.main_layout.addRow(self.right_y_axis_unit_lbl, self.right_y_axis_unit_edt)
        else:
            self.chart.showAxis("right", show=False)

            for i in range(2):
                self.main_layout.removeRow(self.main_layout.rowCount() - 1)

        # Add the Close button back
        self.close_dialog_btn = QPushButton("Close")
        self.close_dialog_btn.clicked.connect(self.handle_close_button_clicked)
        self.main_layout.addRow(None, self.close_dialog_btn)

        self.app.establish_widget_connections(self.main_display)

    def handle_axis_label_change(self, axis_position, new_label, is_unit=False):
        if is_unit:
            self.chart.setLabel(axis_position, units=new_label)
            self.chart.units[axis_position] = new_label
        else:
            if axis_position == "bottom":
                current_label = self.chart.getBottomAxisLabel()
                if X_AXIS_LABEL_SEPARATOR in current_label:
                    current_label = current_label[:current_label.find(X_AXIS_LABEL_SEPARATOR) -
                                                   len(X_AXIS_LABEL_SEPARATOR)]
                new_label = current_label + X_AXIS_LABEL_SEPARATOR + new_label
            self.chart.setLabel(axis_position, text=new_label)
            self.chart.labels[axis_position] = new_label
        return

    def closeEvent(self, event):
        self.handle_close_button_clicked()

    def handle_close_button_clicked(self):
        """
        Close the dialog when the Close button is clicked.
        """
        self.close()
