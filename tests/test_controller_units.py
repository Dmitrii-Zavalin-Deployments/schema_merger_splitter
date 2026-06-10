import json
from unittest.mock import mock_open, patch
import pytest

from src.controller import SchemaMergerSplitterController


# --- 1. Path Resolution Branch Testing (Lines 42, 126) ---

@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_relative_config_path_expansion(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    empty_runs = {"runs": []}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(empty_runs))):
        # Passing a relative path triggers line 42 branch
        result = controller.load_and_evaluate_config("relative/config.json")
        assert result == []


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_relative_input_path_expansion(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    valid_input = {"output_filename": "out.json", "sources": {}}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(valid_input))):
        # Passing a relative path triggers line 126 branch
        out_file, sources = controller.load_input_file("relative/input.json")
        assert out_file == "out.json"
        assert sources == {}


# --- 2. File Not Found Scenarios ---

@patch("pathlib.Path.exists", return_value=False)
def test_config_file_not_found(mock_exists):
    controller = SchemaMergerSplitterController()
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        controller.load_and_evaluate_config("/absolute/missing_config.json")


@patch("pathlib.Path.exists", return_value=False)
def test_input_file_not_found(mock_exists):
    controller = SchemaMergerSplitterController()
    with pytest.raises(FileNotFoundError, match="Input file not found"):
        controller.load_input_file("/absolute/missing_input.json")


# --- 3. Run Configuration Validation Error Paths (Lines 59, 63, 70, 72, 74, 76, 85, 87) ---

@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_missing_runs_field(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps({}))):
        with pytest.raises(ValueError, match="Config missing required field 'runs'"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_runs_field_not_a_list(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps({"runs": "invalid_string_not_list"}))):
        with pytest.raises(ValueError, match="Config field 'runs' must be a list"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_run_missing_requires_all(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_config = {"runs": [{}]}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_config))):
        with pytest.raises(ValueError, match="Config run missing required field 'requires_all'"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_run_missing_requires_none(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_config = {"runs": [{"requires_all": []}]}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_config))):
        with pytest.raises(ValueError, match="Config run missing required field 'requires_none'"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_run_missing_input_file(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_config = {"runs": [{"requires_all": [], "requires_none": []}]}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_config))):
        with pytest.raises(ValueError, match="Config run missing required field 'input_file'"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_run_missing_output_assembler_file(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_config = {"runs": [{"requires_all": [], "requires_none": [], "input_file": "in.json"}]}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_config))):
        with pytest.raises(ValueError, match="Config run missing required field 'output_assembler_file'"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_requires_all_type_check(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_config = {
        "runs": [{
            "requires_all": "not_a_list",
            "requires_none": [],
            "input_file": "in.json",
            "output_assembler_file": "out.json"
        }]
    }
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_config))):
        with pytest.raises(ValueError, match="'requires_all' must be a list"):
            controller.load_and_evaluate_config("/absolute/config.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_config_requires_none_type_check(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_config = {
        "runs": [{
            "requires_all": [],
            "requires_none": "not_a_list",
            "input_file": "in.json",
            "output_assembler_file": "out.json"
        }]
    }
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_config))):
        with pytest.raises(ValueError, match="'requires_none' must be a list"):
            controller.load_and_evaluate_config("/absolute/config.json")


# --- 4. Input File Evaluation Validation Error Paths (Lines 143, 145, 151, 153) ---

@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_input_missing_output_filename_field(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps({}))):
        with pytest.raises(ValueError, match="Input JSON missing required field 'output_filename'"):
            controller.load_input_file("/absolute/input.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_input_missing_sources_field(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps({"output_filename": "out.json"}))):
        with pytest.raises(ValueError, match="Input JSON missing required field 'sources'"):
            controller.load_input_file("/absolute/input.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_input_output_filename_type_check(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_input = {"output_filename": 99999, "sources": {}}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_input))):
        with pytest.raises(ValueError, match="Field 'output_filename' must be a string"):
            controller.load_input_file("/absolute/input.json")


@patch("src.controller.validate")
@patch("pathlib.Path.exists", return_value=True)
def test_input_sources_type_check(mock_exists, mock_validate):
    controller = SchemaMergerSplitterController()
    bad_input = {"output_filename": "out.json", "sources": ["should_be_a_dict_not_list"]}
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(bad_input))):
        with pytest.raises(ValueError, match="Field 'sources' must be a dict"):
            controller.load_input_file("/absolute/input.json")


# --- 5. Conditional Rules Activation Branch Testing (Lines 93-95, 101-103) ---

def test_config_conditional_evaluation_branches():
    controller = SchemaMergerSplitterController()
    runs_payload = {
        "runs": [
            {
                "requires_all": ["present_dependency.txt"],
                "requires_none": ["absent_blocker.txt"],
                "input_file": "activated_run.json",
                "output_assembler_file": "activated_out.json"
            },
            {
                "requires_all": ["missing_dependency.txt"],
                "requires_none": ["present_blocker.txt"],
                "input_file": "skipped_run.json",
                "output_assembler_file": "skipped_out.json"
            }
        ]
    }

    def custom_exists_side_effect(self_path):
        path_str = str(self_path)
        
        print(f"DEBUG: Mock checking path: {path_str}")
        
        # Whitelist the configuration file
        if "config.json" in path_str:
            return True

        # Explicitly define condition mock environments
        if "present_dependency.txt" in path_str:
            return True
        if "present_blocker.txt" in path_str:
            return True
            
        return False

    with patch("src.controller.validate"), \
         patch("pathlib.Path.exists", new=custom_exists_side_effect), \
         patch("pathlib.Path.open", mock_open(read_data=json.dumps(runs_payload))):
         
        activated_pipelines = controller.load_and_evaluate_config("/config/config.json")
        assert activated_pipelines == [("activated_run.json", "activated_out.json")]