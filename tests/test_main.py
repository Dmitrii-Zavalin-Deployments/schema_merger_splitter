from unittest.mock import patch
from src.main import run_pure_pipeline

# -----------------------------------------------------------------------------
# Test Narrative: Main Pipeline Orchestration
# -----------------------------------------------------------------------------
# These tests ensure the orchestrator handles both success states and 
# expected failure modes (like schema validation errors) gracefully.

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