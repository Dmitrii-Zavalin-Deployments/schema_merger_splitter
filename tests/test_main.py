import pytest
from unittest.mock import patch, MagicMock
from src.main import run_pure_pipeline, main

# =============================================================================
# ORCHESTRATION LAYER: run_pure_pipeline
# This section verifies the internal execution chain of the pipeline, 
# ensuring that even if peripheral systems (like receipt validation) fail,
# the core container remains intact.
# =============================================================================

def test_run_pure_pipeline_receipt_failure(tmp_path):
    # Setup the simulation environment and a malformed payload
    input_data = {"sources": {"in.json": [{"from": "$.a", "to": "b"}]}}
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    invalid_receipt_path = simulators_dir / "receipt.json"
    
    # Even if receipt validation raises an exception, the system must 
    # survive and return the processed container.
    with patch("src.main.validate", side_effect=Exception("Schema Invalid")):
        container = run_pure_pipeline(input_data, simulators_dir, "test_output.json", invalid_receipt_path)
    
    # Assert that the container object was returned despite the receipt failure.
    assert container is not None

def test_run_pure_pipeline_happy_path(tmp_path):
    # Verify that a standard execution successfully persists a receipt 
    # and marks the pipeline state as successful.
    input_data = {"sources": {"in.json": [{"from": "$.a", "to": "b"}]}}
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    receipt_path = simulators_dir / "receipt.json"
    
    container = run_pure_pipeline(input_data, simulators_dir, "test_output.json", receipt_path)
    
    # Verify the existence of the receipt file and the state of the container.
    assert receipt_path.exists()
    assert container.success is True


# =============================================================================
# CLI INTERFACE: main()
# This section verifies the CLI contract. It ensures the system handles 
# malformed inputs, missing parameters, and runtime interruptions gracefully.
# =============================================================================

def test_main_missing_arguments():
    # The system must enforce a strict parameter contract. 
    # If the user provides no arguments, the system must exit with code 1.
    with patch("sys.argv", ["src/main.py"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_parse_args_exception():
    # If an unexpected system interruption occurs during argument parsing,
    # the system must catch the RuntimeError and signal failure.
    with patch("argparse.ArgumentParser.parse_args", side_effect=RuntimeError("Forced parsing explosion")):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_integrity_failure(tmp_path):
    # The system must validate the input configuration payload immediately upon load.
    # We provide a malformed (unparseable) JSON file to trigger a failure.
    bad_config = tmp_path / "corrupted_config.json"
    bad_config.write_text("{ unparseable raw payload ...", encoding="utf-8")
    
    with patch("sys.argv", [
        "src/main.py", 
        "--input_output_folder", str(tmp_path), 
        "--input_file", "corrupted_config.json", 
        "--output_file", "out.json"
    ]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_execution_success(tmp_path):
    # When all inputs are valid and the pipeline succeeds, 
    # the entry point must exit with code 0.
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"sources": {}}', encoding="utf-8")
    
    # We mock the return container success status.
    mock_container = MagicMock()
    mock_container.success = True
    
    with patch("sys.argv", [
        "src/main.py", 
        "--input_output_folder", str(tmp_path), 
        "--input_file", "valid_config.json", 
        "--output_file", "out.json"
    ]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        # Exit code 0 implies success.
                        assert exc_info.value.code == 0

def test_main_execution_pipeline_failure(tmp_path):
    # If the pipeline logic fails (e.g., data mapping error),
    # the system must exit with code 1.
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"sources": {}}', encoding="utf-8")
    
    # We mock a container where the operation failed (success=False).
    mock_container = MagicMock()
    mock_container.success = False
    
    with patch("sys.argv", [
        "src/main.py", 
        "--input_output_folder", str(tmp_path), 
        "--input_file", "valid_config.json", 
        "--output_file", "out.json"
    ]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        # Exit code 1 implies logic failure.
                        assert exc_info.value.code == 1