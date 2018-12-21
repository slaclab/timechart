"""
The Main Display Window
"""

import os
import logging

from functools import partial
import datetime

from pyqtgraph import TextItem

from qtpy.QtCore import Qt, Slot, QTimer
from qtpy.QtWidgets import (QApplication, QWidget, QCheckBox, QHBoxLayout,
                            QVBoxLayout, QFormLayout, QLabel, QSplitter,
                            QComboBox, QLineEdit, QPushButton, QSlider,
                            QSpinBox, QTabWidget,
                            QColorDialog, QGroupBox, QRadioButton,
                            QMessageBox, QFileDialog, QScrollArea, QFrame,
                            QSizePolicy, QLayout,
                            QToolButton, QFontDialog)
from qtpy.QtGui import QColor, QPalette

from pydm import Display
from pydm.widgets.timeplot import (PyDMTimePlot, DEFAULT_X_MIN,
                                   MINIMUM_BUFFER_SIZE, DEFAULT_BUFFER_SIZE)
from pydm.utilities.iconfont import IconFont
from ..data_io.settings_importer import SettingsImporter, SettingsImporterException


from .curve_settings_display import CurveSettingsDisplay
from .axis_settings_display import AxisSettingsDisplay
from .chart_data_export_display import ChartDataExportDisplay
from ..utilities.utils import random_color, display_message_box

from .defaults import *
logger = logging.getLogger(__name__)


class TimeChartDisplay(Display):
    def __init__(self, parent=None, args=[], macros=None, show_pv_add_panel=True, config_file=None):
        """
        Create all the widgets, including any child dialogs.

        Parameters
        ----------
        parent : QWidget
            The parent widget of the charting display
        args : list
            The command parameters
        macros : str
            Macros to modify the UI parameters at runtime
        show_pv_add_panel : bool
            Whether or not to show the PV add panel on top of the graph
        """
        super(TimeChartDisplay, self).__init__(parent=parent, args=args,
                                               macros=macros)
        self.legend_font = None
        self.channel_map = dict()
        self.setWindowTitle("TimeChart Tool")

        self.main_layout = QVBoxLayout()
        self.body_layout = QVBoxLayout()

        self.pv_add_panel = QFrame()
        self.pv_add_panel.setVisible(show_pv_add_panel)
        self.pv_add_panel.setMaximumHeight(50)
        self.pv_layout = QHBoxLayout()
        self.pv_name_line_edt = QLineEdit()
        self.pv_name_line_edt.setAcceptDrops(True)
        self.pv_name_line_edt.returnPressed.connect(self.add_curve)

        self.pv_protocol_cmb = QComboBox()
        self.pv_protocol_cmb.addItems(["ca://", "archive://"])
        self.pv_protocol_cmb.setEnabled(False)

        self.pv_connect_push_btn = QPushButton("Connect")
        self.pv_connect_push_btn.clicked.connect(self.add_curve)

        self.tab_panel = QTabWidget()
        self.tab_panel.setMinimumWidth(350)
        self.tab_panel.setMaximumWidth(350)

        self.curve_settings_tab = QWidget()
        self.data_settings_tab = QWidget()
        self.chart_settings_tab = QWidget()

        self.charting_layout = QHBoxLayout()
        self.chart = PyDMTimePlot(plot_by_timestamps=False)
        self.chart.setDownsampling(ds=False, auto=False, mode=None)
        self.chart.plot_redrawn_signal.connect(self.update_curve_data)
        self.chart.setBufferSize(DEFAULT_BUFFER_SIZE)
        self.chart.setPlotTitle(DEFAULT_CHART_TITLE)

        self.splitter = QSplitter()

        self.curve_settings_layout = QVBoxLayout()
        self.curve_settings_layout.setAlignment(Qt.AlignTop)
        self.curve_settings_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.curve_settings_layout.setSpacing(5)

        self.crosshair_settings_layout = QVBoxLayout()
        self.crosshair_settings_layout.setAlignment(Qt.AlignTop)
        self.crosshair_settings_layout.setSpacing(5)

        self.enable_crosshair_chk = QCheckBox("Crosshair")
        self.crosshair_coord_lbl = QLabel()
        self.crosshair_coord_lbl.setWordWrap(True)

        self.curve_settings_inner_frame = QFrame()
        self.curve_settings_inner_frame.setLayout(self.curve_settings_layout)

        self.curve_settings_scroll = QScrollArea()
        self.curve_settings_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded)
        self.curve_settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.curve_settings_scroll.setWidget(self.curve_settings_inner_frame)
        self.curve_settings_scroll.setWidgetResizable(True)

        self.enable_crosshair_chk.setChecked(False)
        self.enable_crosshair_chk.clicked.connect(
            self.handle_enable_crosshair_checkbox_clicked)
        self.enable_crosshair_chk.clicked.emit(False)

        self.curves_tab_layout = QHBoxLayout()
        self.curves_tab_layout.addWidget(self.curve_settings_scroll)

        self.data_tab_layout = QVBoxLayout()
        self.data_tab_layout.setAlignment(Qt.AlignTop)
        self.data_tab_layout.setSpacing(5)

        self.chart_settings_layout = QVBoxLayout()
        self.chart_settings_layout.setAlignment(Qt.AlignTop)
        self.chart_settings_layout.setSpacing(5)

        self.chart_layout = QVBoxLayout()
        self.chart_layout.setSpacing(10)

        self.chart_panel = QWidget()
        self.chart_panel.setMinimumHeight(400)

        self.chart_control_layout = QHBoxLayout()
        self.chart_control_layout.setAlignment(Qt.AlignHCenter)
        self.chart_control_layout.setSpacing(10)
        self.zoom_x_layout = QVBoxLayout()
        self.zoom_x_layout.setAlignment(Qt.AlignTop)
        self.zoom_x_layout.setSpacing(5)

        self.plus_icon = IconFont().icon("plus", color=QColor("green"))
        self.minus_icon = IconFont().icon("minus", color=QColor("red"))
        self.view_all_icon = IconFont().icon("globe", color=QColor("blue"))
        self.reset_icon = IconFont().icon("circle-o-notch",
                                          color=QColor("green"))

        self.zoom_in_x_btn = QPushButton("X Zoom")
        self.zoom_in_x_btn.setIcon(self.plus_icon)
        self.zoom_in_x_btn.clicked.connect(
            partial(self.handle_zoom_in_btn_clicked, "x", True))
        self.zoom_in_x_btn.setEnabled(False)

        self.zoom_out_x_btn = QPushButton("X Zoom")
        self.zoom_out_x_btn.setIcon(self.minus_icon)
        self.zoom_out_x_btn.clicked.connect(
            partial(self.handle_zoom_in_btn_clicked, "x", False))
        self.zoom_out_x_btn.setEnabled(False)

        self.zoom_y_layout = QVBoxLayout()
        self.zoom_y_layout.setAlignment(Qt.AlignTop)
        self.zoom_y_layout.setSpacing(5)

        self.zoom_in_y_btn = QPushButton("Y Zoom")
        self.zoom_in_y_btn.setIcon(self.plus_icon)
        self.zoom_in_y_btn.clicked.connect(
            partial(self.handle_zoom_in_btn_clicked, "y", True))
        self.zoom_in_y_btn.setEnabled(False)

        self.zoom_out_y_btn = QPushButton("Y Zoom")
        self.zoom_out_y_btn.setIcon(self.minus_icon)
        self.zoom_out_y_btn.clicked.connect(
            partial(self.handle_zoom_in_btn_clicked, "y", False))
        self.zoom_out_y_btn.setEnabled(False)

        self.view_all_btn = QPushButton("View All")
        self.view_all_btn.setIcon(self.view_all_icon)
        self.view_all_btn.clicked.connect(self.handle_view_all_button_clicked)
        self.view_all_btn.setEnabled(False)

        self.view_all_reset_chart_layout = QVBoxLayout()
        self.view_all_reset_chart_layout.setAlignment(Qt.AlignTop)
        self.view_all_reset_chart_layout.setSpacing(5)

        self.pause_chart_layout = QVBoxLayout()
        self.pause_chart_layout.setAlignment(Qt.AlignTop)
        self.pause_chart_layout.setSpacing(5)

        self.reset_chart_btn = QPushButton("Reset")
        self.reset_chart_btn.setIcon(self.reset_icon)
        self.reset_chart_btn.clicked.connect(
            self.handle_reset_chart_btn_clicked)
        self.reset_chart_btn.setEnabled(False)

        self.pause_icon = IconFont().icon("pause", color=QColor("red"))
        self.play_icon = IconFont().icon("play", color=QColor("green"))
        self.pause_chart_btn = QPushButton()
        self.pause_chart_btn.setIcon(self.pause_icon)
        self.pause_chart_btn.clicked.connect(
            self.handle_pause_chart_btn_clicked)

        self.title_settings_layout = QVBoxLayout()
        self.title_settings_layout.setAlignment(Qt.AlignTop)
        self.title_settings_layout.setSpacing(5)

        self.title_settings_grpbx = QGroupBox("Title and Legend")
        self.title_settings_grpbx.setMaximumHeight(120)

        self.import_export_data_layout = QVBoxLayout()
        self.import_export_data_layout.setAlignment(Qt.AlignTop)
        self.import_export_data_layout.setSpacing(5)

        self.import_data_btn = QPushButton("Import...")
        self.import_data_btn.clicked.connect(
            self.handle_import_data_btn_clicked)

        self.export_data_btn = QPushButton("Export...")
        self.export_data_btn.clicked.connect(
            self.handle_export_data_btn_clicked)

        self.chart_title_layout = QHBoxLayout()
        self.chart_title_layout.setSpacing(10)

        self.chart_title_lbl = QLabel(text="Graph Title")
        self.chart_title_line_edt = QLineEdit()
        self.chart_title_line_edt.setText(self.chart.getPlotTitle())
        self.chart_title_line_edt.textChanged.connect(
            self.handle_title_text_changed)

        self.chart_title_font_btn = QPushButton()
        self.chart_title_font_btn.setFixedHeight(24)
        self.chart_title_font_btn.setFixedWidth(24)
        self.chart_title_font_btn.setIcon(IconFont().icon("font"))
        self.chart_title_font_btn.clicked.connect(
            partial(self.handle_chart_font_changed, "title")
        )

        self.chart_change_axis_settings_btn = QPushButton(
            text="Change Axis Settings...")
        self.chart_change_axis_settings_btn.clicked.connect(
            self.handle_change_axis_settings_clicked)

        self.update_datetime_timer = QTimer(self)
        self.update_datetime_timer.timeout.connect(
            self.handle_update_datetime_timer_timeout)

        self.chart_sync_mode_layout = QVBoxLayout()
        self.chart_sync_mode_layout.setSpacing(5)

        self.chart_sync_mode_grpbx = QGroupBox("Data Sampling Mode")
        self.chart_sync_mode_grpbx.setMaximumHeight(100)

        self.chart_sync_mode_sync_radio = QRadioButton("Synchronous")
        self.chart_sync_mode_async_radio = QRadioButton("Asynchronous")
        self.chart_sync_mode_async_radio.setChecked(True)

        self.graph_drawing_settings_layout = QVBoxLayout()
        self.graph_drawing_settings_layout.setAlignment(Qt.AlignVCenter)

        self.chart_interval_layout = QFormLayout()

        self.chart_redraw_rate_lbl = QLabel("Redraw Rate (Hz)")
        self.chart_redraw_rate_spin = QSpinBox()
        self.chart_redraw_rate_spin.setRange(MIN_REDRAW_RATE_HZ,
                                             MAX_REDRAW_RATE_HZ)
        self.chart_redraw_rate_spin.setValue(DEFAULT_REDRAW_RATE_HZ)
        self.chart_redraw_rate_spin.editingFinished.connect(
            self.handle_redraw_rate_changed)

        self.chart_data_sampling_rate_lbl = QLabel("Data Sampling Rate (Hz)")
        self.chart_data_async_sampling_rate_spin = QSpinBox()
        self.chart_data_async_sampling_rate_spin.setRange(
            MIN_DATA_SAMPLING_RATE_HZ, MAX_DATA_SAMPLING_RATE_HZ)
        self.chart_data_async_sampling_rate_spin.setValue(
            DEFAULT_DATA_SAMPLING_RATE_HZ)
        self.chart_data_async_sampling_rate_spin.editingFinished.connect(
            self.handle_data_sampling_rate_changed)
        self.chart_data_sampling_rate_lbl.hide()
        self.chart_data_async_sampling_rate_spin.hide()

        self.chart_limit_time_span_layout = QHBoxLayout()
        self.chart_limit_time_span_layout.setSpacing(5)

        self.limit_time_plan_text = "Limit Time Span"
        self.chart_limit_time_span_chk = QCheckBox(self.limit_time_plan_text)
        self.chart_limit_time_span_chk.hide()
        self.chart_limit_time_span_lbl = QLabel("Hr:Min:Sec")
        self.chart_limit_time_span_hours_spin_box = QSpinBox()
        self.chart_limit_time_span_hours_spin_box.setMaximum(999)
        self.chart_limit_time_span_minutes_spin_box = QSpinBox()
        self.chart_limit_time_span_minutes_spin_box.setMaximum(59)
        self.chart_limit_time_span_seconds_spin_box = QSpinBox()
        self.chart_limit_time_span_seconds_spin_box.setMaximum(59)
        self.chart_limit_time_span_activate_btn = QPushButton("Apply")
        self.chart_limit_time_span_activate_btn.setDisabled(True)

        self.chart_ring_buffer_layout = QFormLayout()

        self.chart_ring_buffer_size_lbl = QLabel("Ring Buffer Size")
        self.chart_ring_buffer_size_edt = QLineEdit()
        self.chart_ring_buffer_size_edt.returnPressed.connect(
            self.handle_buffer_size_changed)
        self.chart_ring_buffer_size_edt.setText(str(DEFAULT_BUFFER_SIZE))

        self.show_legend_chk = QCheckBox("Show Legend")
        self.show_legend_chk.clicked.connect(
            self.handle_show_legend_checkbox_clicked)
        self.show_legend_chk.setChecked(self.chart.showLegend)

        self.legend_font_btn = QPushButton()
        self.legend_font_btn.setFixedHeight(24)
        self.legend_font_btn.setFixedWidth(24)
        self.legend_font_btn.setIcon(IconFont().icon("font"))
        self.legend_font_btn.clicked.connect(
            partial(self.handle_chart_font_changed, "legend")
        )

        self.graph_background_color_layout = QFormLayout()
        self.axis_grid_color_layout = QFormLayout()

        self.background_color_lbl = QLabel("Graph Background Color ")
        self.background_color_btn = QPushButton()
        self.background_color_btn.setStyleSheet(
            "background-color: " + self.chart.getBackgroundColor().name())
        self.background_color_btn.setContentsMargins(10, 0, 5, 5)
        self.background_color_btn.setMaximumWidth(20)
        self.background_color_btn.clicked.connect(
            self.handle_background_color_button_clicked)

        self.axis_settings_layout = QVBoxLayout()
        self.axis_settings_layout.setSpacing(10)

        self.show_x_grid_chk = QCheckBox("Show x Grid")
        self.show_x_grid_chk.setChecked(self.chart.showXGrid)
        self.show_x_grid_chk.clicked.connect(
            self.handle_show_x_grid_checkbox_clicked)

        self.show_y_grid_chk = QCheckBox("Show y Grid")
        self.show_y_grid_chk.setChecked(self.chart.showYGrid)
        self.show_y_grid_chk.clicked.connect(
            self.handle_show_y_grid_checkbox_clicked)

        self.axis_color_lbl = QLabel("Axis and Grid Color")
        self.axis_color_btn = QPushButton()
        self.axis_color_btn.setStyleSheet(
            "background-color: " + DEFAULT_CHART_AXIS_COLOR.name())
        self.axis_color_btn.setContentsMargins(10, 0, 5, 5)
        self.axis_color_btn.setMaximumWidth(20)
        self.axis_color_btn.clicked.connect(
            self.handle_axis_color_button_clicked)

        self.grid_opacity_lbl = QLabel("Grid Opacity")
        self.grid_opacity_lbl.setEnabled(False)

        self.grid_opacity_slr = QSlider(Qt.Horizontal)
        self.grid_opacity_slr.setFocusPolicy(Qt.StrongFocus)
        self.grid_opacity_slr.setRange(0, 10)
        self.grid_opacity_slr.setValue(5)
        self.grid_opacity_slr.setTickInterval(1)
        self.grid_opacity_slr.setSingleStep(1)
        self.grid_opacity_slr.setTickPosition(QSlider.TicksBelow)
        self.grid_opacity_slr.valueChanged.connect(
            self.handle_grid_opacity_slider_mouse_release)
        self.grid_opacity_slr.setEnabled(False)

        self.reset_data_settings_btn = QPushButton("Reset Data Settings")
        self.reset_data_settings_btn.clicked.connect(
            self.handle_reset_data_settings_btn_clicked)

        self.reset_chart_settings_btn = QPushButton("Reset Chart Settings")
        self.reset_chart_settings_btn.clicked.connect(
            self.handle_reset_chart_settings_btn_clicked)

        self.curve_checkbox_panel = QWidget()

        self.graph_drawing_settings_grpbx = QGroupBox("Graph Intervals")
        self.graph_drawing_settings_grpbx.setAlignment(Qt.AlignTop)

        self.axis_settings_grpbx = QGroupBox("Graph Appearance")

        self.app = QApplication.instance()
        self.setup_ui()

        self.curve_settings_disp = None
        self.axis_settings_disp = None
        self.chart_data_export_disp = None
        self.chart_data_import_disp = None
        self.grid_alpha = 5
        self.time_span_limit_hours = None
        self.time_span_limit_minutes = None
        self.time_span_limit_seconds = None
        self.data_sampling_mode = ASYNC_DATA_SAMPLING

        # If there is an imported config file, let's start TimeChart with the imported configuration data
        if config_file:
            importer = SettingsImporter(self)
            try:
                importer.import_settings(config_file)
            except SettingsImporterException:
                display_message_box(QMessageBox.Critical, "Import Failure",
                                    "Cannot import the file '{0}'. Check the log for the error details."
                                    .format(config_file))
                logger.exception("Cannot import the file '{0}'.".format(config_file))

    def ui_filepath(self):
        """
        The path to the UI file created by Qt Designer, if applicable.
        """
        # No UI file is being used
        return None

    def ui_filename(self):
        """
        The name the UI file created by Qt Designer, if applicable.
        """
        # No UI file is being used
        return None

    def setup_ui(self):
        """
        Initialize the widgets and layouts.
        """
        self.setLayout(self.main_layout)

        self.pv_layout.addWidget(self.pv_protocol_cmb)
        self.pv_layout.addWidget(self.pv_name_line_edt)
        self.pv_layout.addWidget(self.pv_connect_push_btn)
        self.pv_add_panel.setLayout(self.pv_layout)
        QTimer.singleShot(0, self.pv_name_line_edt.setFocus)

        self.curve_settings_tab.setLayout(self.curves_tab_layout)

        self.chart_settings_tab.setLayout(self.chart_settings_layout)
        self.setup_chart_settings_layout()

        self.data_settings_tab.setLayout(self.data_tab_layout)
        self.setup_data_tab_layout()

        self.tab_panel.addTab(self.curve_settings_tab, "Curves")
        self.tab_panel.addTab(self.data_settings_tab, "Data")
        self.tab_panel.addTab(self.chart_settings_tab, "Graph")

        self.crosshair_settings_layout.addWidget(self.enable_crosshair_chk)
        self.crosshair_settings_layout.addWidget(self.crosshair_coord_lbl)

        self.zoom_x_layout.addWidget(self.zoom_in_x_btn)
        self.zoom_x_layout.addWidget(self.zoom_out_x_btn)

        self.zoom_y_layout.addWidget(self.zoom_in_y_btn)
        self.zoom_y_layout.addWidget(self.zoom_out_y_btn)

        self.view_all_reset_chart_layout.addWidget(self.reset_chart_btn)
        self.view_all_reset_chart_layout.addWidget(self.view_all_btn)

        self.pause_chart_layout.addWidget(self.pause_chart_btn)

        self.import_export_data_layout.addWidget(self.import_data_btn)
        self.import_export_data_layout.addWidget(self.export_data_btn)

        self.chart_control_layout.addLayout(self.zoom_x_layout)
        self.chart_control_layout.addLayout(self.zoom_y_layout)
        self.chart_control_layout.addLayout(self.view_all_reset_chart_layout)
        self.chart_control_layout.addLayout(self.pause_chart_layout)
        self.chart_control_layout.addLayout(self.crosshair_settings_layout)
        self.chart_control_layout.addLayout(self.import_export_data_layout)
        self.chart_control_layout.insertSpacing(5, 30)

        self.chart_layout.addWidget(self.chart)
        self.chart_layout.addLayout(self.chart_control_layout)

        self.chart_panel.setLayout(self.chart_layout)

        self.splitter.addWidget(self.chart_panel)
        self.splitter.addWidget(self.tab_panel)
        self.splitter.setSizes([1, 0])

        self.splitter.setHandleWidth(10)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.charting_layout.addWidget(self.splitter)

        self.body_layout.addWidget(self.pv_add_panel)
        self.body_layout.addLayout(self.charting_layout)
        self.body_layout.setSpacing(0)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.body_layout)

        self.enable_chart_control_buttons(False)

        handle = self.splitter.handle(1)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        button = QToolButton(handle)
        button.setArrowType(Qt.LeftArrow)
        button.clicked.connect(
            lambda: self.handle_splitter_button(True))
        layout.addWidget(button)
        button = QToolButton(handle)
        button.setArrowType(Qt.RightArrow)
        button.clicked.connect(
            lambda: self.handle_splitter_button(False))
        layout.addWidget(button)
        handle.setLayout(layout)

    def handle_splitter_button(self, left=True):
        if left:
            self.splitter.setSizes([1, 1])
        else:
            self.splitter.setSizes([1, 0])

    def change_legend_font(self, font):
        if font is None:
            return
        self.legend_font = font
        items = self.chart.plotItem.legend.items
        for i in items:
            i[1].item.setFont(font)
            i[1].resizeEvent(None)
            i[1].updateGeometry()

    def change_title_font(self, font):
        current_text = self.chart.plotItem.titleLabel.text
        args = {
            "family": font.family,
            "size": "{}pt".format(font.pointSize()),
            "bold": font.bold(),
            "italic": font.italic(),
        }
        self.chart.plotItem.titleLabel.setText(current_text, **args)

    def handle_chart_font_changed(self, target):
        if target not in ("title", "legend"):
            return

        dialog = QFontDialog(self)
        dialog.setOption(QFontDialog.DontUseNativeDialog, True)

        if target == "title":
            dialog.fontSelected.connect(self.change_title_font)
        else:
            dialog.fontSelected.connect(self.change_legend_font)

        dialog.open()

    def setup_data_tab_layout(self):
        self.chart_sync_mode_sync_radio.toggled.connect(
            partial(self.handle_sync_mode_radio_toggle,
                    self.chart_sync_mode_sync_radio))
        self.chart_sync_mode_async_radio.toggled.connect(
            partial(self.handle_sync_mode_radio_toggle,
                    self.chart_sync_mode_async_radio))

        self.chart_sync_mode_layout.addWidget(self.chart_sync_mode_sync_radio)
        self.chart_sync_mode_layout.addWidget(self.chart_sync_mode_async_radio)
        self.chart_sync_mode_grpbx.setLayout(self.chart_sync_mode_layout)

        self.data_tab_layout.addWidget(self.chart_sync_mode_grpbx)

        self.chart_limit_time_span_layout.addWidget(
            self.chart_limit_time_span_lbl)
        self.chart_limit_time_span_layout.addWidget(
            self.chart_limit_time_span_hours_spin_box)
        self.chart_limit_time_span_layout.addWidget(
            self.chart_limit_time_span_minutes_spin_box)
        self.chart_limit_time_span_layout.addWidget(
            self.chart_limit_time_span_seconds_spin_box)
        self.chart_limit_time_span_layout.addWidget(
            self.chart_limit_time_span_activate_btn)

        self.chart_limit_time_span_lbl.hide()
        self.chart_limit_time_span_hours_spin_box.hide()
        self.chart_limit_time_span_minutes_spin_box.hide()
        self.chart_limit_time_span_seconds_spin_box.hide()
        self.chart_limit_time_span_activate_btn.hide()

        self.chart_limit_time_span_hours_spin_box.valueChanged.connect(
            self.handle_time_span_changed)
        self.chart_limit_time_span_minutes_spin_box.valueChanged.connect(
            self.handle_time_span_changed)
        self.chart_limit_time_span_seconds_spin_box.valueChanged.connect(
            self.handle_time_span_changed)

        self.chart_limit_time_span_chk.clicked.connect(
            self.handle_limit_time_span_checkbox_clicked)
        self.chart_limit_time_span_activate_btn.clicked.connect(
            self.handle_chart_limit_time_span_activate_btn_clicked)

        self.chart_interval_layout.addRow(self.chart_redraw_rate_lbl,
                                          self.chart_redraw_rate_spin)
        self.chart_interval_layout.addRow(self.chart_data_sampling_rate_lbl,
                                          self.chart_data_async_sampling_rate_spin)
        self.graph_drawing_settings_layout.addLayout(self.chart_interval_layout)

        self.graph_drawing_settings_layout.addWidget(
            self.chart_limit_time_span_chk)
        self.graph_drawing_settings_layout.addLayout(
            self.chart_limit_time_span_layout)

        self.chart_ring_buffer_layout.addRow(self.chart_ring_buffer_size_lbl,
                                             self.chart_ring_buffer_size_edt)

        self.graph_drawing_settings_layout.addLayout(
            self.chart_ring_buffer_layout)
        self.graph_drawing_settings_grpbx.setLayout(
            self.graph_drawing_settings_layout)

        self.data_tab_layout.addWidget(self.graph_drawing_settings_grpbx)
        self.chart_sync_mode_async_radio.toggled.emit(True)

        self.data_tab_layout.addWidget(self.reset_data_settings_btn)

    def setup_chart_settings_layout(self):
        self.chart_title_layout.addWidget(self.chart_title_lbl)
        self.chart_title_layout.addWidget(self.chart_title_line_edt)
        self.chart_title_layout.addWidget(self.chart_title_font_btn)
        self.title_settings_layout.addLayout(self.chart_title_layout)

        legend_layout = QHBoxLayout()
        legend_layout.addWidget(self.show_legend_chk)
        legend_layout.addWidget(self.legend_font_btn)
        self.title_settings_layout.addLayout(legend_layout)
        self.title_settings_layout.addWidget(
            self.chart_change_axis_settings_btn)
        self.title_settings_grpbx.setLayout(self.title_settings_layout)
        self.chart_settings_layout.addWidget(self.title_settings_grpbx)

        self.graph_background_color_layout.addRow(self.background_color_lbl,
                                                  self.background_color_btn)
        self.axis_settings_layout.addLayout(self.graph_background_color_layout)

        self.axis_grid_color_layout.addRow(self.axis_color_lbl,
                                           self.axis_color_btn)
        self.axis_settings_layout.addLayout(self.axis_grid_color_layout)

        self.axis_settings_layout.addWidget(self.show_x_grid_chk)
        self.axis_settings_layout.addWidget(self.show_y_grid_chk)
        self.axis_settings_layout.addWidget(self.grid_opacity_lbl)
        self.axis_settings_layout.addWidget(self.grid_opacity_slr)

        self.axis_settings_grpbx.setLayout(self.axis_settings_layout)

        self.chart_settings_layout.addWidget(self.axis_settings_grpbx)
        self.chart_settings_layout.addWidget(self.reset_chart_settings_btn)

        self.update_datetime_timer.start(1000)

    def add_curve(self):
        """
        Add a new curve to the chart.
        """
        pv_name = self._get_full_pv_name(self.pv_name_line_edt.text())
        if pv_name and len(pv_name):
            color = random_color(curve_colors_only=True)
            for k, v in self.channel_map.items():
                if color == v.color:
                    color = random_color(curve_colors_only=True)

            self.add_y_channel(pv_name=pv_name, curve_name=pv_name, color=color)
            self.handle_splitter_button(left=True)

    def show_mouse_coordinates(self, x, y):
        self.crosshair_coord_lbl.clear()
        self.crosshair_coord_lbl.setText(
            "x = {0:.3f}\ny = {1:.3f}".format(x, y))

    def handle_enable_crosshair_checkbox_clicked(self, is_checked):
        self.chart.enableCrosshair(is_checked)
        self.crosshair_coord_lbl.setVisible(is_checked)

        self.chart.crosshair_position_updated.connect(
            self.show_mouse_coordinates)

    def add_y_channel(self, pv_name, curve_name, color, line_style=Qt.SolidLine,
                      line_width=2, symbol=None, symbol_size=None, is_visible=True):
        if pv_name in self.channel_map:
            logger.error("'{0}' has already been added.".format(pv_name))
            return

        curve = self.chart.addYChannel(y_channel=pv_name, name=curve_name,
                                       color=color, lineStyle=line_style,
                                       lineWidth=line_width, symbol=symbol,
                                       symbolSize=symbol_size)
        curve.show() if is_visible else curve.hide()

        if self.show_legend_chk.isChecked():
            self.change_legend_font(self.legend_font)
        self.channel_map[pv_name] = curve
        self.generate_pv_controls(pv_name, color)

        self.enable_chart_control_buttons()
        try:
            self.app.add_connection(curve.channel)
        except AttributeError:
            # these methods are not needed on future versions of pydm
            pass

    def generate_pv_controls(self, pv_name, curve_color):
        """
        Generate a set of widgets to manage the appearance of a curve. The set of widgets includes:
            1. A checkbox which shows the curve on the chart if checked, and hide the curve if not
               checked
            2. Three buttons -- Modify..., Focus, and Remove. Modify... will bring up the Curve
               Settings dialog. Focus adjusts the chart's zooming for the current curve.
               Remove will delete the curve from the chart
        Parameters
        ----------
        pv_name: str
            The name of the PV the current curve is being plotted for
        curve_color : QColor
            The color of the curve to paint for the checkbox label to help the user track the curve
            to the checkbox
        """
        individual_curve_layout = QVBoxLayout()

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        size_policy.setHorizontalPolicy(QSizePolicy.Fixed)

        individual_curve_grpbx = QGroupBox()
        individual_curve_grpbx.setMinimumWidth(300)
        individual_curve_grpbx.setMinimumHeight(120)
        individual_curve_grpbx.setAlignment(Qt.AlignTop)

        individual_curve_grpbx.setSizePolicy(size_policy)

        individual_curve_grpbx.setObjectName(pv_name + "_grb")
        individual_curve_grpbx.setLayout(individual_curve_layout)

        checkbox = QCheckBox(parent=individual_curve_grpbx)
        checkbox.setObjectName(pv_name + "_chb")

        palette = checkbox.palette()
        palette.setColor(QPalette.Active, QPalette.WindowText, curve_color)
        checkbox.setPalette(palette)

        display_name = pv_name.split("://")[1]
        if len(display_name) > MAX_DISPLAY_PV_NAME_LENGTH:
            # Only display max allowed number of characters of the PV Name
            display_name = display_name[
                           :int(MAX_DISPLAY_PV_NAME_LENGTH / 2) - 1] + "..." + \
                           display_name[
                           -int(MAX_DISPLAY_PV_NAME_LENGTH / 2) + 2:]

        checkbox.setText(display_name)

        data_text = QLabel(parent=individual_curve_grpbx)
        data_text.setWordWrap(True)
        data_text.setObjectName(pv_name + "_lbl")
        data_text.setPalette(palette)

        checkbox.setChecked(True)
        checkbox.toggled.connect(partial(self.handle_curve_chkbox_toggled, checkbox))
        if not self.chart.findCurve(pv_name).isVisible():
            checkbox.setChecked(False)

        modify_curve_btn = QPushButton("Modify...",
                                       parent=individual_curve_grpbx)
        modify_curve_btn.setObjectName(pv_name + "_btn_modify")
        modify_curve_btn.setMaximumWidth(80)
        modify_curve_btn.clicked.connect(
            partial(self.display_curve_settings_dialog, pv_name))

        focus_curve_btn = QPushButton("Focus", parent=individual_curve_grpbx)
        focus_curve_btn.setObjectName(pv_name + "_btn_focus")
        focus_curve_btn.setMaximumWidth(80)
        focus_curve_btn.clicked.connect(partial(self.focus_curve, pv_name))

        # annotate_curve_btn = QPushButton("Annotate...",
        #                                  parent=individual_curve_grpbx)
        # annotate_curve_btn.setObjectName(pv_name+"_btn_ann")
        # annotate_curve_btn.setMaximumWidth(80)
        # annotate_curve_btn.clicked.connect(
        #     partial(self.annotate_curve, pv_name))

        remove_curve_btn = QPushButton("Remove", parent=individual_curve_grpbx)
        remove_curve_btn.setObjectName(pv_name + "_btn_remove")
        remove_curve_btn.setMaximumWidth(80)
        remove_curve_btn.clicked.connect(partial(self.remove_curve, pv_name))

        curve_btn_layout = QHBoxLayout()
        curve_btn_layout.setSpacing(5)
        curve_btn_layout.addWidget(modify_curve_btn)
        curve_btn_layout.addWidget(focus_curve_btn)
        # curve_btn_layout.addWidget(annotate_curve_btn)
        curve_btn_layout.addWidget(remove_curve_btn)

        individual_curve_layout.addWidget(checkbox)
        individual_curve_layout.addWidget(data_text)
        individual_curve_layout.addLayout(curve_btn_layout)

        self.curve_settings_layout.addWidget(individual_curve_grpbx)

        self.tab_panel.setCurrentIndex(0)

    def handle_curve_chkbox_toggled(self, checkbox):
        """
        Handle a checkbox's checked and unchecked events.

        If a checkbox is checked, find the curve from the channel map. If found, re-draw the curve with its previous
        appearance settings.

        If a checkbox is unchecked, remove the curve from the chart, but keep the cached data in the channel map.

        Parameters
        ----------
        checkbox : QCheckBox
            The current checkbox being toggled
        """
        pv_name = self._get_full_pv_name(checkbox.text())

        if checkbox.isChecked():
            curve = self.channel_map.get(pv_name, None)
            if curve:
                curve.show()
                self.chart.addLegendItem(curve, pv_name,
                                         self.show_legend_chk.isChecked())
                self.change_legend_font(self.legend_font)
        else:
            curve = self.chart.findCurve(pv_name)
            if curve:
                curve.hide()
                self.chart.removeLegendItem(pv_name)

    def display_curve_settings_dialog(self, pv_name):
        """
        Bring up the Curve Settings dialog to modify the appearance of a curve.

        Parameters
        ----------
        pv_name : str
            The name of the PV the curve is being plotted for

        """
        self.curve_settings_disp = CurveSettingsDisplay(self, pv_name)
        self.curve_settings_disp.show()

    def focus_curve(self, pv_name):
        curve = self.chart.findCurve(pv_name)
        if curve:
            self.chart.plotItem.setYRange(curve.minY, curve.maxY, padding=0)

    def annotate_curve(self, pv_name):
        curve = self.chart.findCurve(pv_name)
        if curve:
            annot = TextItem(
                html='<div style="text-align: center"><span style="color: #FFF;">This is the'
                     '</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>',
                anchor=(-0.3, 0.5), border='w', fill=(0, 0, 255, 100))
            self.chart.annotateCurve(curve, annot)

    def remove_curve(self, pv_name):
        """
        Remove a curve from the chart permanently. This will also clear the channel map cache from retaining the
        removed curve's appearance settings.

        Parameters
        ----------
        pv_name : str
            The name of the PV the curve is being plotted for
        """
        curve = self.chart.findCurve(pv_name)
        if curve:
            try:
                self.app.remove_connection(curve.channel)
            except AttributeError:
                # these methods are not needed on future versions of pydm
                pass
            self.chart.removeYChannel(curve)
            del self.channel_map[pv_name]
            self.chart.removeLegendItem(pv_name)

            widget = self.findChild(QGroupBox, pv_name + "_grb")
            if widget:
                widget.deleteLater()

        if len(self.chart.getCurves()) < 1:
            self.enable_chart_control_buttons(False)
            self.show_legend_chk.setChecked(False)

    def handle_title_text_changed(self, new_text):
        self.chart.setPlotTitle(new_text)

    def handle_change_axis_settings_clicked(self):
        self.axis_settings_disp = AxisSettingsDisplay(self)
        self.axis_settings_disp.show()

    def handle_limit_time_span_checkbox_clicked(self, is_checked):
        self.chart_limit_time_span_lbl.setVisible(is_checked)
        self.chart_limit_time_span_hours_spin_box.setVisible(is_checked)
        self.chart_limit_time_span_minutes_spin_box.setVisible(is_checked)
        self.chart_limit_time_span_seconds_spin_box.setVisible(is_checked)
        self.chart_limit_time_span_activate_btn.setVisible(is_checked)

        self.chart_ring_buffer_size_lbl.setDisabled(is_checked)
        self.chart_ring_buffer_size_edt.setDisabled(is_checked)

        if not is_checked:
            self.chart_limit_time_span_chk.setText(self.limit_time_plan_text)

    def handle_time_span_changed(self):
        self.time_span_limit_hours = self.chart_limit_time_span_hours_spin_box.value()
        self.time_span_limit_minutes = self.chart_limit_time_span_minutes_spin_box.value()
        self.time_span_limit_seconds = self.chart_limit_time_span_seconds_spin_box.value()

        status = self.time_span_limit_hours > 0 or self.time_span_limit_minutes > 0 or self.time_span_limit_seconds > 0

        self.chart_limit_time_span_activate_btn.setEnabled(status)

    def handle_chart_limit_time_span_activate_btn_clicked(self):
        timeout_milliseconds = (self.time_span_limit_hours * 3600 + self.time_span_limit_minutes * 60 +
                                self.time_span_limit_seconds) * 1000
        self.chart.setTimeSpan(timeout_milliseconds / 1000.0)
        self.chart_ring_buffer_size_edt.setText(str(self.chart.getBufferSize()))

    def handle_buffer_size_changed(self):
        try:
            new_buffer_size = int(self.chart_ring_buffer_size_edt.text())
            if new_buffer_size and int(new_buffer_size) >= MINIMUM_BUFFER_SIZE:
                self.chart.setBufferSize(new_buffer_size)
        except ValueError:
            display_message_box(QMessageBox.Critical, "Invalid Values",
                                "Only integer values are accepted.")

    def handle_redraw_rate_changed(self):
        self.chart.maxRedrawRate = self.chart_redraw_rate_spin.value()

    def handle_data_sampling_rate_changed(self):
        # The chart expects the value in milliseconds
        sampling_rate_seconds = 1.0 / self.chart_data_async_sampling_rate_spin.value()
        buffer_size = self.chart.getBufferSize()
        self.chart.setUpdateInterval(sampling_rate_seconds)
        if self.chart.getBufferSize() < buffer_size:
            self.chart.setBufferSize(buffer_size)
        self.chart_ring_buffer_size_edt.setText(str(self.chart.getBufferSize()))

    def handle_background_color_button_clicked(self):
        selected_color = QColorDialog.getColor()
        self.chart.setBackgroundColor(selected_color)
        self.background_color_btn.setStyleSheet(
            "background-color: " + selected_color.name())

    def handle_axis_color_button_clicked(self):
        selected_color = QColorDialog.getColor()
        self.chart.setAxisColor(selected_color)
        self.axis_color_btn.setStyleSheet(
            "background-color: " + selected_color.name())

    def handle_grid_opacity_slider_mouse_release(self):
        self.grid_alpha = float(self.grid_opacity_slr.value()) / 10.0
        self.chart.setShowXGrid(self.show_x_grid_chk.isChecked(),
                                self.grid_alpha)
        self.chart.setShowYGrid(self.show_y_grid_chk.isChecked(),
                                self.grid_alpha)

    def handle_show_x_grid_checkbox_clicked(self, is_checked):
        self.chart.setShowXGrid(is_checked, self.grid_alpha)
        self.grid_opacity_lbl.setEnabled(
            is_checked or self.show_y_grid_chk.isChecked())
        self.grid_opacity_slr.setEnabled(
            is_checked or self.show_y_grid_chk.isChecked())

    def handle_show_y_grid_checkbox_clicked(self, is_checked):
        self.chart.setShowYGrid(is_checked, self.grid_alpha)
        self.grid_opacity_lbl.setEnabled(
            is_checked or self.show_x_grid_chk.isChecked())
        self.grid_opacity_slr.setEnabled(
            is_checked or self.show_x_grid_chk.isChecked())

    def handle_show_legend_checkbox_clicked(self, is_checked):
        self.chart.setShowLegend(is_checked)

    def handle_export_data_btn_clicked(self):
        self.chart_data_export_disp = ChartDataExportDisplay(self)
        self.chart_data_export_disp.show()

    def handle_import_data_btn_clicked(self):
        open_file_info = QFileDialog.getOpenFileName(self, caption="Open File", directory=os.path.expanduser('~'),
                                                     filter=IMPORT_FILE_FORMAT)
        open_filename = open_file_info[0]
        if open_filename:
            try:
                importer = SettingsImporter(self)
                importer.import_settings(open_filename)
            except SettingsImporterException:
                display_message_box(QMessageBox.Critical, "Import Failure",
                                    "Cannot import the file '{0}'. Check the log for the error details."
                                    .format(open_filename))
                logger.exception("Cannot import the file '{0}'".format(open_filename))

    def handle_sync_mode_radio_toggle(self, radio_btn):
        if radio_btn.isChecked():
            if radio_btn.text() == "Synchronous":
                self.data_sampling_mode = SYNC_DATA_SAMPLING

                self.chart_data_sampling_rate_lbl.hide()
                self.chart_data_async_sampling_rate_spin.hide()

                self.chart.resetTimeSpan()
                self.chart_limit_time_span_chk.setChecked(False)
                self.chart_limit_time_span_chk.clicked.emit(False)
                self.chart_limit_time_span_chk.hide()

                self.chart.setUpdatesAsynchronously(False)
            elif radio_btn.text() == "Asynchronous":
                self.data_sampling_mode = ASYNC_DATA_SAMPLING

                self.chart_data_sampling_rate_lbl.show()
                self.chart_data_async_sampling_rate_spin.show()
                self.chart_limit_time_span_chk.show()

                self.chart.setUpdatesAsynchronously(True)

    def handle_zoom_in_btn_clicked(self, axis, is_zoom_in):
        scale_factor = 0.5
        if not is_zoom_in:
            scale_factor += 1.0
        if axis == "x":
            self.chart.getViewBox().scaleBy(x=scale_factor)
        elif axis == "y":
            self.chart.getViewBox().scaleBy(y=scale_factor)

    def handle_view_all_button_clicked(self):
        self.chart.plotItem.getViewBox().autoRange()

    def handle_pause_chart_btn_clicked(self):
        if self.chart.pausePlotting():
            self.pause_chart_btn.setIcon(self.pause_icon)
        else:
            self.pause_chart_btn.setIcon(self.play_icon)

    def handle_reset_chart_btn_clicked(self):
        self.chart.getViewBox().setXRange(DEFAULT_X_MIN, 0)
        self.chart.resetAutoRangeY()

    @Slot()
    def handle_reset_chart_settings_btn_clicked(self):
        self.chart.setBackgroundColor(DEFAULT_CHART_BACKGROUND_COLOR)
        self.background_color_btn.setStyleSheet(
            "background-color: " + DEFAULT_CHART_BACKGROUND_COLOR.name())

        self.chart.setAxisColor(DEFAULT_CHART_AXIS_COLOR)
        self.axis_color_btn.setStyleSheet(
            "background-color: " + DEFAULT_CHART_AXIS_COLOR.name())

        self.grid_opacity_slr.setValue(5)

        self.show_x_grid_chk.setChecked(False)
        self.show_x_grid_chk.clicked.emit(False)

        self.show_y_grid_chk.setChecked(False)
        self.show_y_grid_chk.clicked.emit(False)

        self.show_legend_chk.setChecked(False)

        self.chart.setShowXGrid(False)
        self.chart.setShowYGrid(False)
        self.chart.setShowLegend(False)

    @Slot()
    def handle_reset_data_settings_btn_clicked(self):
        self.chart_ring_buffer_size_edt.setText(str(DEFAULT_BUFFER_SIZE))

        self.chart_redraw_rate_spin.setValue(DEFAULT_REDRAW_RATE_HZ)
        self.handle_redraw_rate_changed()

        self.chart_data_async_sampling_rate_spin.setValue(
            DEFAULT_DATA_SAMPLING_RATE_HZ)
        self.chart_data_sampling_rate_lbl.hide()
        self.chart_data_async_sampling_rate_spin.hide()

        self.chart_sync_mode_async_radio.setChecked(True)
        self.chart_sync_mode_async_radio.toggled.emit(True)

        self.chart_limit_time_span_chk.setChecked(False)
        self.chart_limit_time_span_chk.setText(self.limit_time_plan_text)
        self.chart_limit_time_span_chk.clicked.emit(False)

        self.chart.setUpdatesAsynchronously(True)
        self.chart.resetTimeSpan()
        self.chart.resetUpdateInterval()
        self.chart.setBufferSize(DEFAULT_BUFFER_SIZE)

    def enable_chart_control_buttons(self, enabled=True):
        self.zoom_in_x_btn.setEnabled(enabled)
        self.zoom_out_x_btn.setEnabled(enabled)
        self.zoom_in_y_btn.setEnabled(enabled)
        self.zoom_out_y_btn.setEnabled(enabled)

        self.view_all_btn.setEnabled(enabled)
        self.reset_chart_btn.setEnabled(enabled)
        self.pause_chart_btn.setIcon(self.pause_icon)
        self.pause_chart_btn.setEnabled(enabled)
        self.export_data_btn.setEnabled(enabled)

    def _get_full_pv_name(self, pv_name):
        """
        Append the protocol to the PV Name.

        Parameters
        ----------
        pv_name : str
            The name of the PV the curve is being plotted for
        """
        if pv_name and "://" not in pv_name:
            pv_name = ''.join([self.pv_protocol_cmb.currentText(), pv_name])
        return pv_name

    def handle_update_datetime_timer_timeout(self):
        current_label = self.chart.getBottomAxisLabel()
        new_label = "Current Time: " + TimeChartDisplay.get_current_datetime()

        if X_AXIS_LABEL_SEPARATOR in current_label:
            current_label = current_label[
                            current_label.find(X_AXIS_LABEL_SEPARATOR) + len(
                                X_AXIS_LABEL_SEPARATOR):]
            new_label += X_AXIS_LABEL_SEPARATOR + current_label

        self.chart.setLabel("bottom", text=new_label)

    def update_curve_data(self, curve):
        """
        Determine if the PV is active. If not, disable the related PV controls.
        If the PV is active, update the PV controls' states.

        Parameters
        ----------
        curve : PlotItem
           A PlotItem, i.e. a plot, to draw on the chart.
        """
        pv_name = curve.address
        min_y = curve.minY if curve.minY else 0
        max_y = curve.maxY if curve.maxY else 0
        current_y = curve.data_buffer[1, -1]

        grb = self.findChild(QGroupBox, pv_name + "_grb")

        lbl = grb.findChild(QLabel, pv_name + "_lbl")
        lbl.setText("(yMin = {0:.3f}, yMax = {1:.3f}) y = {2:.3f}".format(
            min_y, max_y, current_y))

        chb = grb.findChild(QCheckBox, pv_name + "_chb")

        connected = curve.connected
        if connected and chb.isEnabled():
            return

        chb.setEnabled(connected)
        btn_modify = grb.findChild(QPushButton, pv_name + "_btn_modify")
        btn_modify.setEnabled(connected)
        btn_focus = grb.findChild(QPushButton, pv_name + "_btn_focus")
        btn_focus.setEnabled(connected)

        # btn_ann = grb.findChild(QPushButton, pv_name + "_btn_ann")
        # btn_ann.setEnabled(connected)

    @staticmethod
    def get_current_datetime():
        current_date = datetime.datetime.now().strftime("%b %d, %Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_datetime = current_time + ' (' + current_date + ')'

        return current_datetime

    @property
    def gridAlpha(self):
        return self.grid_alpha
