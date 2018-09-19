# The Main Display Window
from setup_paths import setup_paths
setup_paths()

from functools import partial
import datetime

import numpy as np
from pyqtgraph import TextItem, ViewBox

from pydm import Display
from pydm.widgets.timeplot import PyDMTimePlot, DEFAULT_X_MIN
from data_io.settings_importer import SettingsImporter

from pydmcharting_logging import logging
logger = logging.getLogger(__name__)

from qtpy.QtCore import Qt, QEvent, Slot, QSize, QTimer
from qtpy.QtWidgets import QApplication, QWidget, QCheckBox, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QSplitter,\
    QComboBox, QLineEdit, QPushButton, QSlider, QSpinBox, QTabWidget, QColorDialog, QGroupBox, QRadioButton,\
    QMessageBox, QFileDialog, QScrollArea, QFrame, QSizePolicy, QLayout
from qtpy.QtGui import QColor, QPalette

from displays.curve_settings_display import CurveSettingsDisplay
from displays.axis_settings_display import AxisSettingsDisplay
from displays.chart_data_export_display import ChartDataExportDisplay
from utilities.utils import random_color, display_message_box
from data_io.settings_importer import ASYNC_DATA_SAMPLING, SYNC_DATA_SAMPLING

MINIMUM_BUFFER_SIZE = 1200
MAXIMUM_BUFER_SIZE = 65535
DEFAULT_BUFFER_SIZE = 7200

MIN_REDRAW_RATE_HZ = 1
MAX_REDRAW_RATE_HZ = 240
DEFAULT_REDRAW_RATE_HZ = 30

MIN_DATA_SAMPLING_RATE_HZ = 1
MAX_DATA_SAMPLING_RATE_HZ = 360
DEFAULT_DATA_SAMPLING_RATE_HZ = 10

DEFAULT_CHART_BACKGROUND_COLOR = QColor("black")
DEFAULT_CHART_AXIS_COLOR = QColor("white")

MAX_DISPLAY_PV_NAME_LENGTH = 40

X_AXIS_LABEL_SEPARATOR = " -- "
IMPORT_FILE_FORMAT = "json"


class PyDMChartingDisplay(Display):
    def __init__(self, parent=None, args=[], macros=None):
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
        """
        super(PyDMChartingDisplay, self).__init__(parent=parent, args=args, macros=macros)

        self.channel_map = dict()
        self.setWindowTitle("PyDM Charting Tool")

        self.main_layout = QVBoxLayout()
        self.body_layout = QVBoxLayout()

        self.pv_layout = QHBoxLayout()
        self.pv_name_line_edt = QLineEdit()
        self.pv_name_line_edt.setAcceptDrops(True)
        self.pv_name_line_edt.installEventFilter(self)

        self.pv_protocol_cmb = QComboBox()
        self.pv_protocol_cmb.addItems(["ca://", "archive://"])

        self.pv_connect_push_btn = QPushButton("Connect")
        self.pv_connect_push_btn.clicked.connect(self.add_curve)

        self.tab_panel = QTabWidget()
        self.tab_panel.setMaximumWidth(450)
        self.curve_settings_tab = QWidget()
        self.chart_settings_tab = QWidget()

        self.charting_layout = QHBoxLayout()
        self.chart = PyDMTimePlot(plot_by_timestamps=False, plot_display=self)
        self.chart.setPlotTitle("Time Plot")

        self.splitter = QSplitter()

        self.curve_settings_layout = QVBoxLayout()
        self.curve_settings_layout.setAlignment(Qt.AlignTop)
        self.curve_settings_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.curve_settings_layout.setSpacing(5)

        self.crosshair_settings_layout = QVBoxLayout()
        self.crosshair_settings_layout.setAlignment(Qt.AlignTop)
        self.crosshair_settings_layout.setSpacing(5)

        self.enable_crosshair_chk = QCheckBox("Enable Crosshair")
        self.cross_hair_coord_lbl = QLabel()

        self.curve_settings_inner_frame = QFrame()
        self.curve_settings_inner_frame.setLayout(self.curve_settings_layout)

        self.curve_settings_scroll = QScrollArea()
        self.curve_settings_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.curve_settings_scroll.setWidget(self.curve_settings_inner_frame)

        self.curves_tab_layout = QHBoxLayout()
        self.curves_tab_layout.addWidget(self.curve_settings_scroll)

        self.enable_crosshair_chk.setChecked(False)
        self.enable_crosshair_chk.clicked.connect(self.handle_enable_crosshair_checkbox_clicked)
        self.enable_crosshair_chk.clicked.emit(False)

        self.chart_settings_layout = QVBoxLayout()
        self.chart_settings_layout.setAlignment(Qt.AlignTop)

        self.chart_layout = QVBoxLayout()
        self.chart_panel = QWidget()

        self.chart_control_layout = QHBoxLayout()
        self.chart_control_layout.setAlignment(Qt.AlignHCenter)
        self.chart_control_layout.setSpacing(10)

        self.view_all_btn = QPushButton("View All")
        self.view_all_btn.clicked.connect(self.handle_view_all_button_clicked)
        self.view_all_btn.setEnabled(False)

        self.auto_scale_btn = QPushButton("Auto Scale")
        self.auto_scale_btn.clicked.connect(self.handle_auto_scale_btn_clicked)
        self.auto_scale_btn.setEnabled(False)

        self.reset_chart_btn = QPushButton("Reset")
        self.reset_chart_btn.clicked.connect(self.handle_reset_chart_btn_clicked)
        self.reset_chart_btn.setEnabled(False)

        self.resume_chart_text = "Resume"
        self.pause_chart_text = "Pause"
        self.pause_chart_btn = QPushButton(self.pause_chart_text)
        self.pause_chart_btn.clicked.connect(self.handle_pause_chart_btn_clicked)

        self.title_settings_layout = QVBoxLayout()
        self.title_settings_layout.setSpacing(10)

        self.title_settings_grpbx = QGroupBox()
        self.title_settings_grpbx.setFixedHeight(150)

        self.import_data_btn = QPushButton("Import Data...")
        self.import_data_btn.clicked.connect(self.handle_import_data_btn_clicked)

        self.export_data_btn = QPushButton("Export Data...")
        self.export_data_btn.clicked.connect(self.handle_export_data_btn_clicked)

        self.chart_title_lbl = QLabel(text="Chart Title")
        self.chart_title_line_edt = QLineEdit()
        self.chart_title_line_edt.setText(self.chart.getPlotTitle())
        self.chart_title_line_edt.textChanged.connect(self.handle_title_text_changed)

        self.chart_change_axis_settings_btn = QPushButton(text="Change Axis Settings...")
        self.chart_change_axis_settings_btn.clicked.connect(self.handle_change_axis_settings_clicked)

        self.update_datetime_timer = QTimer(self)
        self.update_datetime_timer.timeout.connect(self.handle_update_datetime_timer_timeout)

        self.chart_sync_mode_layout = QVBoxLayout()
        self.chart_sync_mode_layout.setSpacing(5)

        self.chart_sync_mode_grpbx = QGroupBox("Data Sampling Mode")
        self.chart_sync_mode_grpbx.setFixedHeight(80)

        self.chart_sync_mode_sync_radio = QRadioButton("Synchronous")
        self.chart_sync_mode_async_radio = QRadioButton("Asynchronous")
        self.chart_sync_mode_async_radio.setChecked(True)

        self.graph_drawing_settings_layout = QVBoxLayout()

        self.chart_redraw_rate_lbl = QLabel("Redraw Rate (Hz)")
        self.chart_redraw_rate_spin = QSpinBox()
        self.chart_redraw_rate_spin.setRange(MIN_REDRAW_RATE_HZ, MAX_REDRAW_RATE_HZ)
        self.chart_redraw_rate_spin.setValue(DEFAULT_REDRAW_RATE_HZ)
        self.chart_redraw_rate_spin.valueChanged.connect(self.handle_redraw_rate_changed)

        self.chart_data_sampling_rate_lbl = QLabel("Asynchronous Data Sampling Rate (Hz)")
        self.chart_data_async_sampling_rate_spin = QSpinBox()
        self.chart_data_async_sampling_rate_spin.setRange(MIN_DATA_SAMPLING_RATE_HZ, MAX_DATA_SAMPLING_RATE_HZ)
        self.chart_data_async_sampling_rate_spin.setValue(DEFAULT_DATA_SAMPLING_RATE_HZ)
        self.chart_data_async_sampling_rate_spin.valueChanged.connect(self.handle_data_sampling_rate_changed)
        self.chart_data_sampling_rate_lbl.hide()
        self.chart_data_async_sampling_rate_spin.hide()

        self.chart_limit_time_span_layout = QHBoxLayout()
        self.chart_limit_time_span_layout.setSpacing(5)

        self.limit_time_plan_text = "Limit Time Span"
        self.chart_limit_time_span_chk = QCheckBox(self.limit_time_plan_text)
        self.chart_limit_time_span_chk.hide()
        self.chart_limit_time_span_lbl = QLabel("Hours : Minutes : Seconds")
        self.chart_limit_time_span_hours_line_edt = QLineEdit()
        self.chart_limit_time_span_minutes_line_edt = QLineEdit()
        self.chart_limit_time_span_seconds_line_edt = QLineEdit()
        self.chart_limit_time_span_activate_btn = QPushButton("Apply")
        self.chart_limit_time_span_activate_btn.setDisabled(True)

        self.chart_ring_buffer_size_lbl = QLabel("Ring Buffer Size")
        self.chart_ring_buffer_size_edt = QLineEdit()
        self.chart_ring_buffer_size_edt.installEventFilter(self)
        self.chart_ring_buffer_size_edt.textChanged.connect(self.handle_buffer_size_changed)
        self.chart_ring_buffer_size_edt.setText(str(DEFAULT_BUFFER_SIZE))

        self.show_legend_chk = QCheckBox("Show Legend")
        self.show_legend_chk.setChecked(self.chart.showLegend)
        self.show_legend_chk.clicked.connect(self.handle_show_legend_checkbox_clicked)

        self.graph_background_color_layout = QFormLayout()

        self.background_color_lbl = QLabel("Graph Background Color ")
        self.background_color_btn = QPushButton()
        self.background_color_btn.setStyleSheet("background-color: " + self.chart.getBackgroundColor().name())
        self.background_color_btn.setContentsMargins(10, 0, 5, 5)
        self.background_color_btn.setMaximumWidth(20)
        self.background_color_btn.clicked.connect(self.handle_background_color_button_clicked)

        self.axis_settings_layout = QVBoxLayout()
        self.axis_settings_layout.setSpacing(5)

        self.show_x_grid_chk = QCheckBox("Show x Grid")
        self.show_x_grid_chk.setChecked(self.chart.showXGrid)
        self.show_x_grid_chk.clicked.connect(self.handle_show_x_grid_checkbox_clicked)

        self.show_y_grid_chk = QCheckBox("Show y Grid")
        self.show_y_grid_chk.setChecked(self.chart.showYGrid)
        self.show_y_grid_chk.clicked.connect(self.handle_show_y_grid_checkbox_clicked)

        self.axis_color_lbl = QLabel("Axis and Grid Color")
        self.axis_color_lbl.setEnabled(False)

        self.axis_color_btn = QPushButton()
        self.axis_color_btn.setStyleSheet("background-color: " + DEFAULT_CHART_AXIS_COLOR.name())
        self.axis_color_btn.setContentsMargins(10, 0, 5, 5)
        self.axis_color_btn.setMaximumWidth(20)
        self.axis_color_btn.clicked.connect(self.handle_axis_color_button_clicked)
        self.axis_color_btn.setEnabled(False)

        self.grid_opacity_lbl = QLabel("Grid Opacity")
        self.grid_opacity_lbl.setEnabled(False)

        self.grid_opacity_slr = QSlider(Qt.Horizontal)
        self.grid_opacity_slr.setFocusPolicy(Qt.StrongFocus)
        self.grid_opacity_slr.setRange(0, 10)
        self.grid_opacity_slr.setValue(5)
        self.grid_opacity_slr.setTickInterval(1)
        self.grid_opacity_slr.setSingleStep(1)
        self.grid_opacity_slr.setTickPosition(QSlider.TicksBelow)
        self.grid_opacity_slr.valueChanged.connect(self.handle_grid_opacity_slider_mouse_release)
        self.grid_opacity_slr.setEnabled(False)

        self.reset_chart_settings_btn = QPushButton("Reset Chart Settings")
        self.reset_chart_settings_btn.clicked.connect(self.handle_reset_chart_settings_btn_clicked)

        self.curve_checkbox_panel = QWidget()

        self.graph_drawing_settings_grpbx = QGroupBox()
        self.graph_drawing_settings_grpbx.setFixedHeight(270)

        self.axis_settings_grpbx = QGroupBox()
        self.axis_settings_grpbx.setFixedHeight(180)

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

    def minimumSizeHint(self):
        """
        The minimum recommended size of the main window.
        """
        return QSize(1490, 800)

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
        QTimer.singleShot(0, self.pv_name_line_edt.setFocus)

        self.curve_settings_tab.setLayout(self.curves_tab_layout)
        self.chart_settings_tab.setLayout(self.chart_settings_layout)
        self.setup_chart_settings_layout()

        self.tab_panel.addTab(self.curve_settings_tab, "Curves")
        self.tab_panel.addTab(self.chart_settings_tab, "Chart")
        self.tab_panel.hide()

        self.crosshair_settings_layout.addWidget(self.enable_crosshair_chk)
        self.crosshair_settings_layout.addWidget(self.cross_hair_coord_lbl)

        self.chart_control_layout.addWidget(self.auto_scale_btn)
        self.chart_control_layout.addWidget(self.view_all_btn)
        self.chart_control_layout.addWidget(self.reset_chart_btn)
        self.chart_control_layout.addWidget(self.pause_chart_btn)
        self.chart_control_layout.addLayout(self.crosshair_settings_layout)
        self.chart_control_layout.addWidget(self.import_data_btn)
        self.chart_control_layout.addWidget(self.export_data_btn)

        self.chart_control_layout.setStretch(4, 15)
        self.chart_control_layout.insertSpacing(5, 350)

        self.chart_layout.addWidget(self.chart)
        self.chart_layout.addLayout(self.chart_control_layout)

        self.chart_panel.setLayout(self.chart_layout)

        self.splitter.addWidget(self.chart_panel)
        self.splitter.addWidget(self.tab_panel)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.charting_layout.addWidget(self.splitter)

        self.body_layout.addLayout(self.pv_layout)
        self.body_layout.addLayout(self.charting_layout)
        self.body_layout.addLayout(self.chart_control_layout)
        self.main_layout.addLayout(self.body_layout)

        self.enable_chart_control_buttons(False)

    def setup_chart_settings_layout(self):
        self.chart_sync_mode_sync_radio.toggled.connect(partial(self.handle_sync_mode_radio_toggle,
                                                                self.chart_sync_mode_sync_radio))
        self.chart_sync_mode_async_radio.toggled.connect(partial(self.handle_sync_mode_radio_toggle,
                                                                 self.chart_sync_mode_async_radio))

        self.title_settings_layout.addWidget(self.chart_title_lbl)
        self.title_settings_layout.addWidget(self.chart_title_line_edt)
        self.title_settings_layout.addWidget(self.show_legend_chk)
        self.title_settings_layout.addWidget(self.chart_change_axis_settings_btn)
        self.title_settings_grpbx.setLayout(self.title_settings_layout)
        self.chart_settings_layout.addWidget(self.title_settings_grpbx)

        self.chart_sync_mode_layout.addWidget(self.chart_sync_mode_sync_radio)
        self.chart_sync_mode_layout.addWidget(self.chart_sync_mode_async_radio)
        self.chart_sync_mode_grpbx.setLayout(self.chart_sync_mode_layout)
        self.chart_settings_layout.addWidget(self.chart_sync_mode_grpbx)

        self.chart_settings_layout.addWidget(self.chart_sync_mode_grpbx)

        self.chart_limit_time_span_layout.addWidget(self.chart_limit_time_span_lbl)
        self.chart_limit_time_span_layout.addWidget(self.chart_limit_time_span_hours_line_edt)

        self.chart_limit_time_span_layout.addWidget(self.chart_limit_time_span_minutes_line_edt)
        self.chart_limit_time_span_layout.addWidget(self.chart_limit_time_span_seconds_line_edt)
        self.chart_limit_time_span_layout.addWidget(self.chart_limit_time_span_activate_btn)

        self.chart_limit_time_span_lbl.hide()
        self.chart_limit_time_span_hours_line_edt.hide()
        self.chart_limit_time_span_minutes_line_edt.hide()
        self.chart_limit_time_span_seconds_line_edt.hide()
        self.chart_limit_time_span_activate_btn.hide()

        self.chart_limit_time_span_hours_line_edt.textChanged.connect(self.handle_time_span_edt_text_changed)
        self.chart_limit_time_span_minutes_line_edt.textChanged.connect(self.handle_time_span_edt_text_changed)
        self.chart_limit_time_span_seconds_line_edt.textChanged.connect(self.handle_time_span_edt_text_changed)

        self.chart_limit_time_span_chk.clicked.connect(self.handle_limit_time_span_checkbox_clicked)
        self.chart_limit_time_span_activate_btn.clicked.connect(self.handle_chart_limit_time_span_activate_btn_clicked)
        self.chart_limit_time_span_activate_btn.installEventFilter(self)

        self.graph_background_color_layout.addRow(self.background_color_lbl, self.background_color_btn)

        self.graph_drawing_settings_layout.addLayout(self.graph_background_color_layout)
        self.graph_drawing_settings_layout.addWidget(self.chart_redraw_rate_lbl)
        self.graph_drawing_settings_layout.addWidget(self.chart_redraw_rate_spin)
        self.graph_drawing_settings_layout.addWidget(self.chart_data_sampling_rate_lbl)
        self.graph_drawing_settings_layout.addWidget(self.chart_data_async_sampling_rate_spin)
        self.graph_drawing_settings_layout.addWidget(self.chart_limit_time_span_chk)
        self.graph_drawing_settings_layout.addLayout(self.chart_limit_time_span_layout)
        self.graph_drawing_settings_layout.addWidget(self.chart_ring_buffer_size_lbl)
        self.graph_drawing_settings_layout.addWidget(self.chart_ring_buffer_size_edt)
        self.graph_drawing_settings_grpbx.setLayout(self.graph_drawing_settings_layout)

        self.axis_settings_layout.addWidget(self.show_x_grid_chk)
        self.axis_settings_layout.addWidget(self.show_y_grid_chk)
        self.axis_settings_layout.addWidget(self.axis_color_lbl)
        self.axis_settings_layout.addWidget(self.axis_color_btn)
        self.axis_settings_layout.addWidget(self.grid_opacity_lbl)
        self.axis_settings_layout.addWidget(self.grid_opacity_slr)
        self.axis_settings_grpbx.setLayout(self.axis_settings_layout)

        self.chart_settings_layout.addWidget(self.graph_drawing_settings_grpbx)
        self.chart_settings_layout.addWidget(self.axis_settings_grpbx)
        self.chart_settings_layout.addWidget(self.reset_chart_settings_btn)

        self.chart_sync_mode_async_radio.toggled.emit(True)
        self.update_datetime_timer.start(1000)

    def eventFilter(self, obj, event):
        """
        Handle key and mouse events for any applicable widget.

        Parameters
        ----------
        obj : QWidget
            The current widget that accepts the event
        event : QEvent
            The key or mouse event to handle

        Returns
        -------
            True if the event was handled successfully; False otherwise
        """
        if obj == self.pv_name_line_edt and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.add_curve()
                return True
        elif obj == self.chart_limit_time_span_activate_btn and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.handle_chart_limit_time_span_activate_btn_clicked()
                return True
        elif obj == self.chart_ring_buffer_size_edt:
            if event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) or \
                    event.type() == QEvent.FocusOut:
                try:
                    buffer_size = int(self.chart_ring_buffer_size_edt.text())
                    if buffer_size < MINIMUM_BUFFER_SIZE:
                        self.chart_ring_buffer_size_edt.setText(str(MINIMUM_BUFFER_SIZE))
                except ValueError:
                    display_message_box(QMessageBox.Critical, "Invalid Values",  "Only integer values are accepted.")
                return True
        return super(PyDMChartingDisplay, self).eventFilter(obj, event)

    def add_curve(self):
        """
        Add a new curve to the chart.
        """
        pv_name = self._get_full_pv_name(self.pv_name_line_edt.text())
        color = random_color()
        for k, v in self.channel_map.items():
            if color == v.color:
                color = random_color()

        self.add_y_channel(pv_name=pv_name, curve_name=pv_name, color=color)

    def handle_enable_crosshair_checkbox_clicked(self, is_checked):
        self.chart.enableCrosshair(is_checked)
        self.cross_hair_coord_lbl.setVisible(is_checked)

    def add_y_channel(self, pv_name, curve_name, color, line_style=Qt.SolidLine, line_width=2, symbol=None,
                      symbol_size=None):
        if pv_name in self.channel_map:
            logger.error("'{0}' has already been added.".format(pv_name))
            return

        curve = self.chart.addYChannel(y_channel=pv_name, name=curve_name, color=color, lineStyle=line_style,
                                       lineWidth=line_width, symbol=symbol, symbolSize=symbol_size)
        self.channel_map[pv_name] = curve
        self.generate_pv_controls(pv_name, color)

        self.enable_chart_control_buttons()
        self.app.establish_widget_connections(self)

    def generate_pv_controls(self, pv_name, curve_color):
        """
        Generate a set of widgets to manage the appearance of a curve. The set of widgets includes:
            1. A checkbox which shows the curve on the chart if checked, and hide the curve if not checked
            2. Two buttons -- Modify... and Remove. Modify... will bring up the Curve Settings dialog. Remove will
               delete the curve from the chart
        This set of widgets will be hidden initially, until the first curve is plotted.

        Parameters
        ----------
        pv_name: str
            The name of the PV the current curve is being plotted for

        curve_color : QColor
            The color of the curve to paint for the checkbox label to help the user track the curve to the checkbox
        """
        checkbox = QCheckBox()
        checkbox.setObjectName(pv_name)

        palette = checkbox.palette()
        palette.setColor(QPalette.Active, QPalette.WindowText, curve_color)
        checkbox.setPalette(palette)

        display_name = pv_name.split("://")[1]
        if len(display_name) > MAX_DISPLAY_PV_NAME_LENGTH:
            # Only display max allowed number of characters of the PV Name
            display_name = display_name[:int(MAX_DISPLAY_PV_NAME_LENGTH / 2) - 1] + "..." + \
                           display_name[-int(MAX_DISPLAY_PV_NAME_LENGTH / 2) + 2:]

        checkbox.setText(display_name)

        data_text = QLabel()
        data_text.setObjectName(pv_name)
        data_text.setPalette(palette)

        checkbox.setChecked(True)
        checkbox.clicked.connect(partial(self.handle_curve_chkbox_toggled, checkbox))

        curve_btn_layout = QHBoxLayout()

        modify_curve_btn = QPushButton("Modify...")
        modify_curve_btn.setObjectName(pv_name)
        modify_curve_btn.setMaximumWidth(100)
        modify_curve_btn.clicked.connect(partial(self.display_curve_settings_dialog, pv_name))

        focus_curve_btn = QPushButton("Focus")
        focus_curve_btn.setObjectName(pv_name)
        focus_curve_btn.setMaximumWidth(100)
        focus_curve_btn.clicked.connect(partial(self.focus_curve, pv_name))

        annotate_curve_btn = QPushButton("Annotate...")
        annotate_curve_btn.setObjectName(pv_name)
        annotate_curve_btn.setMaximumWidth(100)
        annotate_curve_btn.clicked.connect(partial(self.annotate_curve, pv_name))

        remove_curve_btn = QPushButton("Remove")
        remove_curve_btn.setObjectName(pv_name)
        remove_curve_btn.setMaximumWidth(100)
        remove_curve_btn.clicked.connect(partial(self.remove_curve, pv_name))

        curve_btn_layout.addWidget(modify_curve_btn)
        curve_btn_layout.addWidget(focus_curve_btn)
        curve_btn_layout.addWidget(annotate_curve_btn)
        curve_btn_layout.addWidget(remove_curve_btn)

        individual_curve_layout = QVBoxLayout()
        individual_curve_layout.addWidget(checkbox)
        individual_curve_layout.addWidget(data_text)
        individual_curve_layout.addLayout(curve_btn_layout)

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Fixed)
        individual_curve_grpbx = QGroupBox()
        individual_curve_grpbx.setSizePolicy(size_policy)

        individual_curve_grpbx.setObjectName(pv_name)
        individual_curve_grpbx.setLayout(individual_curve_layout)

        self.curve_settings_layout.addWidget(individual_curve_grpbx)
        self.tab_panel.show()

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
                self.chart.addLegendItem(curve, pv_name, self.show_legend_chk.isChecked())
                curve.show()
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
            annot = TextItem(html='<div style="text-align: center"><span style="color: #FFF;">This is the'
                                  '</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>',
                             anchor=(-0.3, 0.5), border='w', fill=(0, 0, 255, 100))
            annot = TextItem("test", anchor=(-0.3, 0.5))
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
            self.chart.removeYChannel(curve)
            del self.channel_map[pv_name]
            self.chart.removeLegendItem(pv_name)

            widgets = self.findChildren((QCheckBox, QLabel, QPushButton, QGroupBox), pv_name)
            for w in widgets:
                w.deleteLater()

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
        self.chart_limit_time_span_hours_line_edt.setVisible(is_checked)
        self.chart_limit_time_span_minutes_line_edt.setVisible(is_checked)
        self.chart_limit_time_span_seconds_line_edt.setVisible(is_checked)
        self.chart_limit_time_span_activate_btn.setVisible(is_checked)

        self.chart_ring_buffer_size_lbl.setDisabled(is_checked)
        self.chart_ring_buffer_size_edt.setDisabled(is_checked)

        if not is_checked:
            self.chart_limit_time_span_chk.setText(self.limit_time_plan_text)

    def handle_time_span_edt_text_changed(self, new_text):
        try:
            self.time_span_limit_hours = int(self.chart_limit_time_span_hours_line_edt.text())
            self.time_span_limit_minutes = int(self.chart_limit_time_span_minutes_line_edt.text())
            self.time_span_limit_seconds = int(self.chart_limit_time_span_seconds_line_edt.text())
        except ValueError as e:
            self.time_span_limit_hours = None
            self.time_span_limit_minutes = None
            self.time_span_limit_seconds = None

        if self.time_span_limit_hours is not None and self.time_span_limit_minutes is not None and \
                self.time_span_limit_seconds is not None:
            self.chart_limit_time_span_activate_btn.setEnabled(True)
        else:
            self.chart_limit_time_span_activate_btn.setEnabled(False)

    def handle_chart_limit_time_span_activate_btn_clicked(self):
        if self.time_span_limit_hours is None or self.time_span_limit_minutes is None or \
                self.time_span_limit_seconds is None:
            display_message_box(QMessageBox.Critical, "Invalid Values",
                                "Hours, minutes, and seconds expect only integer values.")
        else:
            timeout_milliseconds = (self.time_span_limit_hours * 3600 + self.time_span_limit_minutes * 60 +
                                    self.time_span_limit_seconds) * 1000
            self.chart.setTimeSpan(timeout_milliseconds / 1000.0)
            self.chart_ring_buffer_size_edt.setText(str(self.chart.getBufferSize()))

    def handle_buffer_size_changed(self, new_buffer_size):
        try:
            if new_buffer_size and int(new_buffer_size) > MINIMUM_BUFFER_SIZE:
                self.chart.setBufferSize(new_buffer_size)
        except ValueError:
            display_message_box(QMessageBox.Critical, "Invalid Values", "Only integer values are accepted.")

    def handle_redraw_rate_changed(self, new_redraw_rate):
        self.chart.maxRedrawRate = new_redraw_rate

    def handle_data_sampling_rate_changed(self, new_data_sampling_rate):
        # The chart expects the value in milliseconds
        sampling_rate_seconds = 1 / new_data_sampling_rate
        self.chart.setUpdateInterval(sampling_rate_seconds)

    def handle_background_color_button_clicked(self):
        selected_color = QColorDialog.getColor()
        self.chart.setBackgroundColor(selected_color)
        self.background_color_btn.setStyleSheet("background-color: " + selected_color.name())

    def handle_axis_color_button_clicked(self):
        selected_color = QColorDialog.getColor()
        self.chart.setAxisColor(selected_color)
        self.axis_color_btn.setStyleSheet("background-color: " + selected_color.name())

    def handle_grid_opacity_slider_mouse_release(self):
        self.grid_alpha = float(self.grid_opacity_slr.value()) / 10.0
        self.chart.setShowXGrid(self.show_x_grid_chk.isChecked(), self.grid_alpha)
        self.chart.setShowYGrid(self.show_y_grid_chk.isChecked(), self.grid_alpha)

    def handle_show_x_grid_checkbox_clicked(self, is_checked):
        self.chart.setShowXGrid(is_checked, self.grid_alpha)

        self.axis_color_lbl.setEnabled(is_checked or self.show_y_grid_chk.isChecked())
        self.axis_color_btn.setEnabled(is_checked or self.show_y_grid_chk.isChecked())
        self.grid_opacity_lbl.setEnabled(is_checked or self.show_y_grid_chk.isChecked())
        self.grid_opacity_slr.setEnabled(is_checked or self.show_y_grid_chk.isChecked())

    def handle_show_y_grid_checkbox_clicked(self, is_checked):
        self.chart.setShowYGrid(is_checked, self.grid_alpha)

        self.axis_color_lbl.setEnabled(is_checked or self.show_x_grid_chk.isChecked())
        self.axis_color_btn.setEnabled(is_checked or self.show_x_grid_chk.isChecked())
        self.grid_opacity_lbl.setEnabled(is_checked or self.show_x_grid_chk.isChecked())
        self.grid_opacity_slr.setEnabled(is_checked or self.show_x_grid_chk.isChecked())

    def handle_show_legend_checkbox_clicked(self, is_checked):
        self.chart.setShowLegend(is_checked)

    def handle_export_data_btn_clicked(self):
        self.chart_data_export_disp = ChartDataExportDisplay(self)
        self.chart_data_export_disp.show()

    def handle_import_data_btn_clicked(self):
        open_file_info = QFileDialog.getOpenFileName(self, caption="Save File", filter="*." + IMPORT_FILE_FORMAT)
        open_file_name = open_file_info[0]
        if open_file_name:
            importer = SettingsImporter(self)
            importer.import_settings(open_file_name)

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
                self.graph_drawing_settings_grpbx.setFixedHeight(180)

                self.chart.setUpdatesAsynchronously(False)
            elif radio_btn.text() == "Asynchronous":
                self.data_sampling_mode = ASYNC_DATA_SAMPLING

                self.chart_data_sampling_rate_lbl.show()
                self.chart_data_async_sampling_rate_spin.show()
                self.chart_limit_time_span_chk.show()
                self.graph_drawing_settings_grpbx.setFixedHeight(270)

                self.chart.setUpdatesAsynchronously(True)
        self.app.establish_widget_connections(self)

    def handle_auto_scale_btn_clicked(self):
        self.chart.resetAutoRangeX()
        self.chart.resetAutoRangeY()

    def handle_view_all_button_clicked(self):
        self.chart.getViewBox().autoRange()

    def handle_pause_chart_btn_clicked(self):
        if self.chart.pausePlotting():
            self.pause_chart_btn.setText(self.pause_chart_text)
        else:
            self.pause_chart_btn.setText(self.resume_chart_text)

    def handle_reset_chart_btn_clicked(self):
        self.chart.getViewBox().setXRange(DEFAULT_X_MIN, 0)
        self.chart.resetAutoRangeY()

    @Slot()
    def handle_reset_chart_settings_btn_clicked(self):
        self.chart_ring_buffer_size_edt.setText(str(DEFAULT_BUFFER_SIZE))

        self.chart_redraw_rate_spin.setValue(DEFAULT_REDRAW_RATE_HZ)
        self.chart_data_async_sampling_rate_spin.setValue(DEFAULT_DATA_SAMPLING_RATE_HZ)
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

        self.chart.setBackgroundColor(DEFAULT_CHART_BACKGROUND_COLOR)
        self.background_color_btn.setStyleSheet("background-color: " + DEFAULT_CHART_BACKGROUND_COLOR.name())

        self.chart.setAxisColor(DEFAULT_CHART_AXIS_COLOR)
        self.axis_color_btn.setStyleSheet("background-color: " + DEFAULT_CHART_AXIS_COLOR.name())

        self.grid_opacity_slr.setValue(5)

        self.show_x_grid_chk.setChecked(False)
        self.show_x_grid_chk.clicked.emit(False)

        self.show_y_grid_chk.setChecked(False)
        self.show_y_grid_chk.clicked.emit(False)

        self.show_legend_chk.setChecked(False)

        self.chart.setShowXGrid(False)
        self.chart.setShowYGrid(False)
        self.chart.setShowLegend(False)

    def enable_chart_control_buttons(self, enabled=True):
        self.auto_scale_btn.setEnabled(enabled)
        self.view_all_btn.setEnabled(enabled)
        self.reset_chart_btn.setEnabled(enabled)
        self.pause_chart_btn.setText(self.pause_chart_text)
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
        new_label = "Current Time: " + PyDMChartingDisplay.get_current_datetime()

        if X_AXIS_LABEL_SEPARATOR in current_label:
            current_label = current_label[current_label.find(X_AXIS_LABEL_SEPARATOR) + len(X_AXIS_LABEL_SEPARATOR):]
            new_label += X_AXIS_LABEL_SEPARATOR + current_label

        self.chart.setLabel("bottom", text=new_label)

    def update_curve_data(self, curve):
        """
        Determine if the PV is active. If not, disable the related PV controls. If the PV is active, update the PV
        controls' states.

        Parameters
        ----------
        curve : PlotItem
           A PlotItem, i.e. a plot, to draw on the chart.
        """
        pv_name = curve.name()
        max_x = self.chart.getViewBox().viewRange()[1][0]
        max_y = self.chart.getViewBox().viewRange()[1][1]
        current_y = curve.data_buffer[1, -1]

        widgets = self.findChildren((QCheckBox, QLabel, QPushButton), pv_name)
        for w in widgets:
            if np.isnan(current_y):
                if isinstance(w, QCheckBox):
                    w.setChecked(False)
            else:
                if isinstance(w, QCheckBox) and not w.isEnabled():
                    w.setChecked(True)
                if isinstance(w, QLabel):
                    w.clear()
                    w.setText("(yMin = {0:.3f}, yMax = {1:.3f}) y = {2:.3f}".format(max_x, max_y, current_y))
                    w.show()
            w.setEnabled(not np.isnan(current_y))

            if isinstance(w, QPushButton) and w.text() == "Remove":
                # Enable the Remove button to make removing inactive PVs possible anytime
                w.setEnabled(True)

    def show_mouse_coordinates(self, x, y):
        self.cross_hair_coord_lbl.clear()
        self.cross_hair_coord_lbl.setText("x = {0:.3f}, y = {1:.3f}".format(x, y))

    @staticmethod
    def get_current_datetime():
        current_date = datetime.datetime.now().strftime("%b %d, %Y")
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_datetime = current_time + ' (' + current_date + ')'

        return current_datetime

    @property
    def gridAlpha(self):
        return self.grid_alpha
