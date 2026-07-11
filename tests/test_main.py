import pytest
from unittest.mock import patch, MagicMock
from src.main import run_pure_pipeline, main

# -----------------------------------------------------------------------------
# Test Narrative: Main Pipeline Orchestration & CLI Entrypoint
# -----------------------------------------------------------------------------

# We simulate a scenario where output schema validation fails.
# This forces the pipeline to hit the 'except' block during receipt generation.
def test_run_pure_pipeline_receipt_failure(tmp_path):
    # We define the input configuration for the test pipeline.
    input_data = {
        "output_filename": "test_output.json",
        "sources": {"in.json": [{"from": "$.a", "to": "b"}]}
    }
    
    # We create the necessary input environment within the temporary directory.
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    
    # We identify the path where the invalid receipt will be generated.
    invalid_receipt_path = simulators_dir / "receipt.json"
    
    # We mock the validation function to raise an Exception, simulating a validation failure.
    with patch("src.main.validate", side_effect=Exception("Schema Invalid")):
        # We execute the pipeline orchestration.
        container = run_pure_pipeline(input_data, simulators_dir, invalid_receipt_path)
    
    # We assert that the container object is returned, verifying the process continued.
    assert container is not None

# We validate the successful execution flow through the pipeline.
def test_run_pure_pipeline_happy_path(tmp_path):
    # We configure the valid input data structure.
    input_data = {
        "output_filename": "test_output.json",
        "sources": {"in.json": [{"from": "$.a", "to": "b"}]}
    }
    
    # We prepare the file system state.
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    receipt_path = simulators_dir / "receipt.json"
    
    # We run the pipeline and capture the resulting container state.
    container = run_pure_pipeline(input_data, simulators_dir, receipt_path)
    
    # We assert that the receipt file exists and the container indicates success.
    assert receipt_path.exists()
    assert container.success is True

# We invoke main() without command-line arguments.
# This tests the boundary condition where the application must log an error and exit.
def test_main_missing_arguments():
    # We mock sys.argv to simulate an execution with missing arguments.
    with patch("sys.argv", ["src/main.py"]):
        # We assert that the system exits with a status code of 1.
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

# We simulate a scenario where the inbound configuration file causes an exception.
# This might occur due to corrupted JSON formatting or schema validation mismatches.
def test_main_integrity_failure(tmp_path):
    # We create a corrupted configuration file.
    bad_config = tmp_path / "corrupted_config.json"
    bad_config.write_text("{ unparseable raw payload ...", encoding="utf-8")
    
    # We mock the CLI arguments to point to this corrupt file.
    with patch("sys.argv", ["src/main.py", str(bad_config)]):
        # We assert that the application catches the error and exits with status code 1.
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

# We perform a full execution path from the CLI entrypoint where the configuration is valid.
def test_main_execution_success(tmp_path):
    # We write a valid configuration file to the test directory.
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"output_filename": "out.json", "sources": {}}', encoding="utf-8")
    
    # We mock the internal state of the container to simulate a successful pipeline run.
    mock_container = MagicMock()
    mock_container.success = True
    
    # We mock the environment to simulate a successful CLI invocation.
    with patch("sys.argv", ["src/main.py", str(valid_config)]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"output_filename": "out.json", "sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        # We assert that the main process exits with status code 0.
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 0

# We perform a full execution path where the core pipeline processing encounters errors.
def test_main_execution_pipeline_failure(tmp_path):
    # We write a valid configuration file.
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"output_filename": "out.json", "sources": {}}', encoding="utf-8")
    
    # We mock the container to simulate a failed processing state.
    mock_container = MagicMock()
    mock_container.success = False
    
    # We mock the environment.
    with patch("sys.argv", ["src/main.py", str(valid_config)]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"output_filename": "out.json", "sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        # We assert that the process exits with status code 1.
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 1