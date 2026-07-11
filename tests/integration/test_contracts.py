import json
from pathlib import Path
from src.main import run_pure_pipeline

# -----------------------------------------------------------------------------
# Test Narrative: Data Contract Structural Validation
# -----------------------------------------------------------------------------
# These tests enforce the shape of data before any computation occurs.
# We utilize dummy JSON files located in data/testing-input-output/.

def test_input_contract_parity():
    # We define the required schema fields for the Sovereign Container.
    required_fields = {"p1", "p2", "v1", "v2", "h1", "h2"}
    
    # Path to our dummy data
    input_path = Path("data/testing-input-output/validation_input_1.json")
    
    # Load and validate
    data = json.loads(input_path.read_text())
    
    # The set of keys in the input must be a superset of required_fields.
    missing = required_fields - set(data.keys())
    assert len(missing) == 0, f"Input Contract Violation: Missing fields {missing}"

def test_results_contract_parity():
    # Define pipeline inputs and base path for readability
        pipeline_config = {
            "output_filename": "validation_output.json",
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
    project_base = Path("data/testing-input-output/")
        
    # Execute pipeline
    run_pure_pipeline(pipeline_config, project_base)
    
    # We verify the output structure contains the projected computational results.
    required_results = {"p_min", "p_max", "v_min", "v_max", "h"}
    
    # Using the result of our pipeline logic
    output_path = Path("data/testing-input-output/validation_output.json")
    
    # Structural assertion: If the output doesn't exist or is malformed, fail immediately.
    assert output_path.exists(), "Results Contract Violation: Output missing."
    data = json.loads(output_path.read_text())
    
    for field in required_results:
        assert field in data, f"Results Contract Violation: Field '{field}' missing."