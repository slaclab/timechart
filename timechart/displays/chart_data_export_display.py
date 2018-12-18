"""
The Dialog to Export Data from a Chart
"""

import os

from qtpy.QtCore import Qt, QSize
from qtpy.QtWidgets import (QVBoxLayout, QFormLayout, QCheckBox, QLineEdit,
                            QFileDialog, QLabel, QComboBox,
                            QPushButton, QColorDialog, QMessageBox)
from qtpy.QtGui import QColor

from pyqtgraph.exporters import CSVExporter, ImageExporter
from pyqtgraph.parametertree import Parameter

from pydm import Display
from ..data_io.settings_exporter import SettingsExporter
from ..utilities.utils import display_message_box

from .defaults import (DEFAULT_EXPORTED_IMAGE_WIDTH, DEFAULT_EXPORTED_IMAGE_HEIGHT)


class TimeChartImageExporter(ImageExporter):
    """
    Override the buggy widthChanged and heightChanged settings from pyqtgraph
    """

    def __init__(self, item):
        super(TimeChartImageExporter, self).__init__(item=item)

    def widthChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.height()) / sr.width()
        self.params.param('height').setValue(int(self.params['width'] * ar))

    def heightChanged(self):
        sr = self.getSourceRect()
        ar = float(sr.width()) / sr.height()
        self.params.param('width').setValue(int(self.params['height'] * ar))


class ChartDataExportDisplay(Display):
    def __init__(self, main_display, parent=None):
        super(ChartDataExportDisplay, self).__init__(parent=parent)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(5)
        self.main_display = main_display

        self.export_options_lbl = QLabel()
        self.export_options_lbl.setText("Export Options")
        self.export_options_cmb = QComboBox()
        self.export_options_cmb.addItems(
            ("Curve Data", "Chart Settings", "Image File"))
        self.export_options_cmb.currentIndexChanged.connect(
            self.handle_export_options_index_changed)

        # Options for Chart Settings
        self.include_pv_chk = QCheckBox("Include currently plotted PVs")
        self.include_pv_chk.setChecked(True)

        self.include_chart_settings_chk = QCheckBox(
            "Include current chart settings")
        self.include_chart_settings_chk.setChecked(True)

        # Options for Image File
        self.image_dimension_layout = QFormLayout()
        self.image_dimension_layout.setSpacing(10)

        self.image_width_lbl = QLabel("Image width")
        self.image_width_edt = QLineEdit()
        self.image_width_edt.editingFinished.connect(
            self.handle_image_dimension_value)
        self.image_width_edt.setText(DEFAULT_EXPORTED_IMAGE_WIDTH)

        self.image_height_lbl = QLabel("Image height")
        self.image_height_edt = QLineEdit()
        self.image_height_edt.editingFinished.connect(
            self.handle_image_dimension_value)
        self.image_height_edt.setText(DEFAULT_EXPORTED_IMAGE_HEIGHT)

        self.anti_alias_chk = QCheckBox("Anti-alias")
        self.anti_alias_chk.setChecked(True)

        self.export_image_background_color_lbl = QLabel("Background Color ")
        self.export_image_background_btn = QPushButton()
        self.export_image_background_btn.setMaximumWidth(20)
        self.export_image_background_btn.setStyleSheet(
            "background-color: black")
        self.export_image_background_btn.clicked.connect(
            self.handle_export_image_background_button_clicked)

        self.export_format_lbl = QLabel()
        self.export_format_lbl.setText("Export Format")
        self.file_format_cmb = QComboBox()
        self.file_format_cmb.addItems(("csv", "json", "png"))
        self.file_format = ""
        self.exported_image_background_color = QColor(Qt.black)

        self.save_file_btn = QPushButton("Export...")
        self.save_file_btn.clicked.connect(self.handle_save_file_btn_clicked)

        self.image_width = 0
        self.image_height = 0

        self.setFixedSize(QSize(300, 150))
        self.setWindowTitle("Export Chart Data")
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
        self.main_layout.addWidget(self.export_options_lbl)
        self.main_layout.addWidget(self.export_options_cmb)
        self.main_layout.addWidget(self.include_pv_chk)
        self.main_layout.addWidget(self.include_chart_settings_chk)

        self.image_dimension_layout.addRow(self.image_width_lbl,
                                           self.image_width_edt)
        self.image_dimension_layout.addRow(self.image_height_lbl,
                                           self.image_height_edt)
        self.main_layout.addLayout(self.image_dimension_layout)

        self.main_layout.addWidget(self.anti_alias_chk)
        self.main_layout.addWidget(self.export_image_background_color_lbl)
        self.main_layout.addWidget(self.export_image_background_btn)
        self.main_layout.addWidget(self.export_format_lbl)
        self.main_layout.addWidget(self.file_format_cmb)
        self.main_layout.addWidget(self.save_file_btn)
        self.setLayout(self.main_layout)

        self.export_options_cmb.currentIndexChanged.emit(0)

        self.image_width_edt.editingFinished.emit()
        self.image_height_edt.editingFinished.emit()

    def handle_export_options_index_changed(self, selected_index):
        if selected_index == 0:
            self.setFixedSize(QSize(300, 150))
            self.main_layout.setAlignment(Qt.AlignTop)
        elif selected_index == 1:
            self.setFixedSize(QSize(300, 200))
            self.main_layout.setAlignment(Qt.AlignTop)
        elif selected_index == 2:
            self.setFixedSize(QSize(300, 300))
            self.main_layout.setAlignment(Qt.AlignVCenter)

        self.include_pv_chk.setVisible(selected_index == 1)
        self.include_chart_settings_chk.setVisible(selected_index == 1)

        self.image_width_lbl.setVisible(selected_index == 2)
        self.image_width_edt.setVisible(selected_index == 2)
        self.image_height_lbl.setVisible(selected_index == 2)
        self.image_height_edt.setVisible(selected_index == 2)
        self.anti_alias_chk.setVisible(selected_index == 2)
        self.export_image_background_color_lbl.setVisible(selected_index == 2)
        self.export_image_background_btn.setVisible(selected_index == 2)

        self.file_format = ""
        self.file_format_cmb.setCurrentIndex(selected_index)
        supported_formats = self.file_format_cmb.currentText().split(",")
        for f in supported_formats:
            self.file_format += "*." + f + ";;"
        self.file_format = self.file_format[:-2]
        self.file_format_cmb.setEnabled(False)

    def handle_save_file_btn_clicked(self):
        saved_file_info = QFileDialog.getSaveFileName(
            self, caption="Save File", directory=os.path.expanduser('~'),
            filter=self.file_format)
        saved_file_name = saved_file_info[0]
        if saved_file_info[1][1:] not in saved_file_name:
            saved_file_name += saved_file_info[1][1:]

        if saved_file_name:
            if self.export_options_cmb.currentIndex() == 0:
                data_exporter = CSVExporter(self.main_display.chart.plotItem)
                data_exporter.export(saved_file_name)
            elif self.export_options_cmb.currentIndex() == 2:
                image_exporter = TimeChartImageExporter(
                    self.main_display.chart.plotItem)
                image_exporter.params = Parameter(name='params', type='group',
                                                  children=[
                                                      {'name': 'width',
                                                       'type': 'int',
                                                       'value': self.image_width,
                                                       'limits': (0, None)},
                                                      {'name': 'height',
                                                       'type': 'int',
                                                       'value': self.image_height,
                                                       'limits': (0, None)},
                                                      {'name': 'antialias',
                                                       'type': 'bool',
                                                       'value': True},
                                                      {'name': 'background',
                                                       'type': 'color',
                                                       'value': self.exported_image_background_color},
                                                  ])

                image_exporter.widthChanged()
                image_exporter.heightChanged()
                image_exporter.export(fileName=saved_file_name)
            else:
                settings_exporter = SettingsExporter(self.main_display,
                                                     self.include_pv_chk.isChecked(),
                                                     self.include_chart_settings_chk.isChecked())
                settings_exporter.export_settings(saved_file_name)

            self.close()
            QMessageBox.information(self, "Data Export", "Data exported successfully!")

    def handle_export_image_background_button_clicked(self):
        self.exported_image_background_color = QColorDialog.getColor()
        self.export_image_background_btn.setStyleSheet("background-color: " +
                                                       self.exported_image_background_color.name())

    def handle_image_dimension_value(self):
        image_width = self.image_width_edt.text()
        image_height = self.image_height_edt.text()
        try:
            if image_width:
                self.image_width = int(image_width)
                if self.image_width <= 0:
                    raise ValueError
            if image_height:
                self.image_height = int(image_height)
                if self.image_height <= 0:
                    raise ValueError
            elif not image_width and not image_height:
                raise ValueError
        except ValueError:
            display_message_box(QMessageBox.Critical, "Invalid Values",
                                "Only integer values larger than 0 are accepted.")
