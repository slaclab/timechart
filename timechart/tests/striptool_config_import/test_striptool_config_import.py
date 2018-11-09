# Unit Test for StripTool Config File Importing

import pytest

import os
from os.path import isfile
import json
import difflib

import logging
logger = logging.getLogger(__name__)

from pydm.utilities.colors import svg_color_from_hex

from timechart.data_io.import_strategies.striptool_import_strategy import StripToolImportStrategy
from timechart.data_io.import_strategies.settings_import_strategy import SettingsImportStrategy


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
    input_dir_path = "data"

    try:
        os.makedirs("output")
    except os.error as err:
        # It's OK if the directory exists. This is to be compatible with Python 2.7
        if err.errno != os.errno.EEXIST:
            raise err
    output_dir_path = "output"

    import_strategy = StripToolImportStrategy(None)

    def mock_apply_settings(timechart_settings, main_display=None):
        logger.info("Applying settings to Main Display...")

        _serialize_colors(timechart_settings)
        del timechart_settings["__version__"]

        # Dump converted contents into a JSON file
        output_filename = striptool_filename + ".json"
        with open(os.path.join(output_dir_path, output_filename), 'w') as json_file:
            json.dump(timechart_settings, json_file, separators=(',', ':'), indent=4)

        # Compare the output file to the expected file
        _compare_with_expected_output(output_dir_path, output_filename)

    monkeypatch.setattr(SettingsImportStrategy, "apply_settings", mock_apply_settings)

    striptool_filenames = [f for f in os.listdir(input_dir_path) if isfile(os.path.join(
        input_dir_path, f))]
    for striptool_filename in striptool_filenames:
        # Import each StripTool config file for conversion to TimeChart configurations
        import_strategy.import_file(os.path.join(input_dir_path, striptool_filename))


def _serialize_colors(timechart_settings):
    """
    Helper method to serialize QColor objects to string, useful for dumping converted contents into
    a JSON file.

    Parameters
    ----------
    timechart_settings : OrderDict
        The dictionary containing the converted configuration data.
    """
    for k, v in timechart_settings.items():
        if isinstance(timechart_settings[k], dict):
            _serialize_colors(timechart_settings[k])
        elif "color" in k and v is not None:
            timechart_settings[k] = str(svg_color_from_hex(v.name(), hex_on_fail=True))


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
    expected_output_dir_path = "expected_output"

    with open(os.path.join(output_dir_path, output_filename), 'r') as output:
        with open(os.path.join(expected_output_dir_path, output_filename), 'r') as expected_output:
            diffs = difflib.unified_diff(output.readlines(), expected_output.readlines(),
                                         fromfile="converted_output",
                                         tofile="expected_output")
            diff_lines = []
            for line in diffs:
                diff_lines.append(line)

            assert len(diff_lines) == 0
