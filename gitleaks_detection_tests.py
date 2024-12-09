import pytest
import subprocess
import json
from pathlib import Path

SCRIPT_PATH = "gitleaks_detection.py"


# Helper function to read the output file
def read_output_file(path):
    output_path = Path(path)
    if output_path.exists():
        with output_path.open("r") as f:
            return json.load(f)
    return None


# Test cases
def test_valid_arguments_with_findings():
    args = [
        "python", SCRIPT_PATH,
        "-s", "/Users/omar-veedy/PycharmProjects/fake-public-secrets",
        "-rp", "output77.json",
        "gitleaks", "detect"
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0
    output = read_output_file("output77.json")
    assert "findings" in output
    assert isinstance(output["findings"], list)


def test_valid_arguments_with_additional_args():
    args = [
        "python", SCRIPT_PATH,
        "-s", "/Users/omar-veedy/PycharmProjects/fake-public-secrets",
        "-rp", "output77.json",
        "gitleaks", "detect", "--no-git"
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0
    output = read_output_file("output77.json")
    assert "findings" in output
    assert isinstance(output["findings"], list)


def test_invalid_argument_unknown_flag():
    args = [
        "python", SCRIPT_PATH,
        "-s", "/Users/omar-veedy/PycharmProjects/fake-public-secrets",
        "-rp", "output77.json",
        "gitleaks", "detect", "--jit"
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 126
    output = read_output_file("output77.json")
    assert output["exit_code"] == 2
    assert "unknown argument '--jit'" in output["error_message"]


def test_missing_source_argument():
    args = [
        "python", SCRIPT_PATH,
        "-rp", "output.json",
        "gitleaks", "detect"
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 2
    output = read_output_file("output.json")
    assert output["exit_code"] == 2
    assert "please provide a source folder" in output["error_message"]


def test_invalid_source_path():
    args = [
        "python", SCRIPT_PATH,
        "-s", "/Users/omar-veedy/PycharmProjects/fake",
        "-rp", "output.json",
        "gitleaks", "detect"
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 2
    output = read_output_file("output.json")
    assert output["exit_code"] == 2
    assert "please provide a valid source folder" in output["error_message"]


def test_missing_command_and_subcommand_with_additional_args():
    args = [
        "python", SCRIPT_PATH,
        "-s", "/Users/omar-veedy/PycharmProjects/fake-public-secrets",
        "-rp", "output.json",
        "--no-git"
    ]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 2
    output = read_output_file("output.json")
    assert output["exit_code"] == 2
    assert "unrecognized arguments: --no-git" in output["error_message"]


def test_help_command():
    args = ["python", SCRIPT_PATH, "-h"]
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage: gitleaks_detection.py" in result.stdout
    assert "Run Gitleaks and process its output" in result.stdout


# Fixture to clean up output files after tests
@pytest.fixture(autouse=True)
def cleanup():
    yield
    output_files = ["output77.json", "output.json"]
    for file in output_files:
        path = Path(file)
        if path.exists():
            path.unlink()
