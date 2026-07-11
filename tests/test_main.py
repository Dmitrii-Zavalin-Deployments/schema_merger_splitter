import pytest
from unittest.mock import patch, MagicMock
from src.main import run_pure_pipeline, main

# -----------------------------------------------------------------------------
# Test Narrative: Main Pipeline Orchestration & CLI Entrypoint
# -----------------------------------------------------------------------------
# These tests ensure the orchestrator handles both internal pipeline executions
# and outer CLI boundary conditions (arguments, initialization, and exit codes).

def test_run_pure_pipeline_receipt_failure(tmp_path):
    # [The Scenario]: We simulate a scenario where the output schema validation 
    # fails, forcing the pipeline to hit the 'except' block in receipt generation.
    
    # 1. Setup dummy configuration
    input_data = {
        "output_filename": "test_output.json",
        "sources": {"in.json": [{"from": "$.a", "to": "b"}]}
    }
    
    # Create valid dummy input/schema files in temp dir
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    
    # 2. Define path for a non-existent or invalid schema
    invalid_receipt_path = simulators_dir / "receipt.json"
    
    # 3. Execution: Run the pipeline
    # We expect the pipeline to complete (returning a container), but log the error
    # triggered by the missing output schema validation path.
    with patch("src.main.validate", side_effect=Exception("Schema Invalid")):
        container = run_pure_pipeline(input_data, simulators_dir, invalid_receipt_path)
    
    # 4. Assert: Container should still exist as logic executed
    assert container is not None

def test_run_pure_pipeline_happy_path(tmp_path):
    # [The Scenario]: Validate successful execution flow through the pipeline.
    
    input_data = {
        "output_filename": "test_output.json",
        "sources": {"in.json": [{"from": "$.a", "to": "b"}]}
    }
    
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    receipt_path = simulators_dir / "receipt.json"
    
    # Note: We assume the existing schema files are available in the repo root
    # during CI execution.
    container = run_pure_pipeline(input_data, simulators_dir, receipt_path)
    
    assert receipt_path.exists()
    assert container.success is True


def test_main_missing_arguments():
    # [Scenario: Line 71-73]: Invoke main() with no command line configuration path.
    # The application must log an error and exit with status code 1.
    with patch("sys.argv", ["src/main.py"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_integrity_failure(tmp_path):
    # [Scenario: Line 97-99]: Inbound configuration file mapping causes an exception
    # (e.g., corrupted JSON formatting or schema validation mismatch).
    bad_config = tmp_path / "corrupted_config.json"
    bad_config.write_text("{ unparseable raw payload ...", encoding="utf-8")
    
    with patch("sys.argv", ["src/main.py", str(bad_config)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_execution_success(tmp_path):
    # [Scenario: Line 103 (Success Branch)]: Full execution path from CLI entrypoint.
    # Config file maps cleanly, pipeline executes successfully, and returns exit code 0.
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"output_filename": "out.json", "sources": {}}', encoding="utf-8")
    
    mock_container = MagicMock()
    mock_container.success = True
    
    with patch("sys.argv", ["src/main.py", str(valid_config)]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"output_filename": "out.json", "sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 0


def test_main_execution_pipeline_failure(tmp_path):
    # [Scenario: Line 103 (Failure Branch)]: Full execution path from CLI entrypoint
    # where the core pipeline processing encounters errors, producing an exit code 1.
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"output_filename": "out.json", "sources": {}}', encoding="utf-8")
    
    mock_container = MagicMock()
    mock_container.success = False
    
    with patch("sys.argv", ["src/main.py", str(valid_config)]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"output_filename": "out.json", "sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 1