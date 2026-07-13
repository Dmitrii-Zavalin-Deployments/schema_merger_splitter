import json
from pathlib import Path
from src.main import run_pure_pipeline

# =============================================================================
# INPUT CONTRACT TRACK: Schema Parity
# This section verifies that source data files maintain the strict interface 
# required by the transformation logic before ingestion.
# =============================================================================

def test_input_contract_parity():
    # Define the mandatory fields required by the processing engine.
    required_fields = {"p1", "p2", "v1", "v2", "h1", "h2"}
    
    # Load the raw source file from the project data directory.
    input_path = Path("data/testing-input-output/validation_input_1.json")
    data = json.loads(input_path.read_text())
    
    # Identify any fields missing from the data against the required contract.
    missing = required_fields - set(data.keys())
    
    # Verify parity: if the length of missing fields is not zero, the contract is broken.
    assert len(missing) == 0, f"Input Contract Violation: Missing fields {missing}"


# =============================================================================
# INTEGRATION CONTRACT TRACK: End-to-End Pipeline
# This section validates that the execution engine successfully maps inputs 
# to outputs and preserves the expected schema in the generated artifacts.
# =============================================================================

def test_results_contract_parity():
    # Construct the pipeline configuration defining source-to-target extraction rules.
    pipeline_config = {
        "sources": {
            "validation_input_1.json": [
                {"from": "$.p2", "to": "p_min"},
                {"from": "$.p1", "to": "p_max"}
            ],
            "validation_input_2.json": [
                {"from": "$.velocity.v1", "to": "v_min"},
                {"from": "$.velocity.v2", "to": "v_max"},
                {"from": "$.height.h1", "to": "h"}
            ]
        }
    }
    
    # Prepare workspace path context for the pipeline execution.
    project_base = Path("data/testing-input-output/")
    receipt_path = project_base / "test_execution_receipt.json"
    
    # Execute the pure pipeline logic, explicitly passing the required output filename.
    run_pure_pipeline(pipeline_config, project_base, "validation_output.json", receipt_path)
    
    # Define the mandatory keys that must exist in the final product.
    required_results = {"p_min", "p_max", "v_min", "v_max", "h"}
    output_path = Path("data/testing-input-output/validation_output.json")
    
    # Assert existence of the output file produced by the pipeline.
    assert output_path.exists(), "Results Contract Violation: Output missing."
    
    # Load generated output data for field validation.
    data = json.loads(output_path.read_text())
    
    # Iterate through required keys to ensure they are present in the final JSON.
    for field in required_results:
        assert field in data, f"Results Contract Violation: Field '{field}' missing."

    # Cleanup: Remove the temporary execution receipt file to keep the test environment pristine.
    if receipt_path.exists():
        receipt_path.unlink()