import json
from pathlib import Path
from src.main import run_pure_pipeline

def test_input_contract_parity():
    required_fields = {"p1", "p2", "v1", "v2", "h1", "h2"}
    input_path = Path("data/testing-input-output/validation_input_1.json")
    data = json.loads(input_path.read_text())
    missing = required_fields - set(data.keys())
    assert len(missing) == 0, f"Input Contract Violation: Missing fields {missing}"

def test_results_contract_parity():
    # Adjusted to match schema removal of output_filename
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
    project_base = Path("data/testing-input-output/")
    receipt_path = project_base / "test_execution_receipt.json"
    
    # Execute pipeline passing the newly decoupled output filename argument explicitly
    run_pure_pipeline(pipeline_config, project_base, "validation_output.json", receipt_path)
    
    required_results = {"p_min", "p_max", "v_min", "v_max", "h"}
    output_path = Path("data/testing-input-output/validation_output.json")
    
    assert output_path.exists(), "Results Contract Violation: Output missing."
    data = json.loads(output_path.read_text())
    
    for field in required_results:
        assert field in data, f"Results Contract Violation: Field '{field}' missing."

    if receipt_path.exists():
        receipt_path.unlink()