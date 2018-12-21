"""
Unit Test for StripTool Config File Importing
"""

import pytest

import os
try:
    from os import errno
except ImportError:
    # For Python 3.7
    import errno

from os.path import isfile
import json
import difflib

from qtpy.QtGui import QColor

from timechart.data_io.settings_importer import SettingsImporter
from timechart.data_io.importers.timechart_config_importer import TimeChartConfigImporter
from timechart.utilities import utils

import logging
logger = logging.getLogger(__name__)


TEST_DIR_PATH = os.path.join(os.getcwd(),'timechart', 'tests', 'striptool_config_import')
INPUT_DIR_PATH = os.path.join(TEST_DIR_PATH, 'data')
OUTPUT_DIR_PATH = os.path.join(TEST_DIR_PATH, 'output')
EXPECTED_OUTPUT_DIR_PATH = os.path.join(TEST_DIR_PATH, 'expected_output')


def test_import_striptool_file(monkeypatch):
    """
    Import all StripTool config files, one-by-one, from the "data" directory, then convert and dump
    the converted contents as JSON files, and then compare those files with the expected output
    JSON files.

    Parameters
    ----------
    monkeypatch : fixture
        To override the apply_settings method in TimeChartImportStrategy, making it a method to dump
        out converted contents as JSON files, and compare those files to the expected.

    """
    _make_output_dir()

    def mock_apply_settings(_, timechart_settings):
        logger.info("Applying settings to Main Display...")

        utils.serialize_colors(timechart_settings)
        del timechart_settings["__version__"]

        # Dump converted contents into a JSON file
        output_filename = striptool_filename + ".json"
        with open(os.path.join(OUTPUT_DIR_PATH, output_filename), 'w') as json_file:
            json.dump(timechart_settings, json_file, separators=(',', ':'), indent=4)

        # Compare the output file to the expected file
        _compare_with_expected_output(OUTPUT_DIR_PATH, output_filename)

    monkeypatch.setattr(TimeChartConfigImporter, "apply_settings", mock_apply_settings)

    settings_importer = SettingsImporter(None)

    striptool_filenames = [f for f in os.listdir(INPUT_DIR_PATH) if isfile(os.path.join(
        INPUT_DIR_PATH, f))]
    for striptool_filename in striptool_filenames:
        # Import each StripTool config file for conversion to TimeChart configurations
        settings_importer.import_settings(os.path.join(INPUT_DIR_PATH, striptool_filename))


def test_export_converted_files():
    """
    Import all StripTool config files, one-by-one, from the "data" directory, convert the StripTool config data into
    the TimeChart config data, and save the data as JSON files.

    This test executes a different code path then the previous test, i.e. testing the convert_stp_file method with the
    path to export a TimeChart JSON config file as the second parameter.
    """
    settings_importer = SettingsImporter()
    _make_output_dir()

    striptool_filenames = [f for f in os.listdir(INPUT_DIR_PATH) if isfile(os.path.join(
        INPUT_DIR_PATH, f))]
    for striptool_filename in striptool_filenames:
        with open(os.path.join(INPUT_DIR_PATH, striptool_filename), 'r') as input_file:
            output_filename = striptool_filename + ".json"
            settings_importer.convert_stp_file(input_file, os.path.join(OUTPUT_DIR_PATH, output_filename))


@pytest.mark.parametrize("is_curve_color, randomized_color", [
    (True, QColor("red")),
    (False, QColor("red")),
    (True, QColor("black")),
    (True, QColor("white")),
    (False, QColor("black")),
    (False, QColor("white")),
])
def test_random_color(monkeypatch, is_curve_color, randomized_color):
    true_pick_random_color = utils.pick_random_color

    def mock_pick_random_color():
        if is_curve_color and randomized_color in (QColor("black"), QColor("white")):
            return true_pick_random_color()
        return randomized_color

    monkeypatch.setattr(utils, "pick_random_color", mock_pick_random_color)
    picked_color = utils.random_color(is_curve_color)

    if is_curve_color:
        assert picked_color not in (QColor("black"), QColor("white"))
        if randomized_color not in (QColor("black"), QColor("white")):
            assert picked_color == randomized_color
    else:
        assert picked_color == randomized_color


def _compare_with_expected_output(output_dir_path, output_filename):
    """
    Helper method to compare the converted contents to the expected. These are in the form of JSON
    files.

    Parameters
    ----------
    output_dir_path : str
        The path to the directory containing the converted contents, saved as a JSON file
    output_filename : str
        The name of the JSON file, containing the converted configuration data.
    """
    with open(os.path.join(output_dir_path, output_filename), 'r') as output:
        with open(os.path.join(EXPECTED_OUTPUT_DIR_PATH, output_filename), 'r') as expected_output:
            diffs = difflib.unified_diff(output.readlines(), expected_output.readlines(),
                                         fromfile="converted_output",
                                         tofile="expected_output")
            diff_lines = []
            for line in diffs:
                diff_lines.append(line)

            assert len(diff_lines) == 0


def _make_output_dir():
    """
    Make a directory to store test output files. These files will be compared with the expected output files.
    """
    try:
        os.makedirs(OUTPUT_DIR_PATH)
    except os.error as err:
        # It's OK if the directory exists. This is to be compatible with Python 2.7
        if err.errno != errno.EEXIST:
            raise err
