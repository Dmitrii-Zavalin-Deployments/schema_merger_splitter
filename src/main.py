import sys
import json
import logging
from pathlib import Path
from jsonschema import validate
from src.state.merger_splitter_state import MergerSplitterState
from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from interfaces.pipeline_interfaces import PipelineInterface

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("main")

def run_pure_pipeline(input_data: dict, simulators_dir: Path, execution_receipt_path: Path) -> PipelineInterface:
    """
    Direct Orchestration Context: Constructs the Sovereign Container 
    and steps through the execution chain without configuration layers.
    """
    repo_root = Path(__file__).resolve().parents[1]
    results_schema_path = repo_root / "schema" / "schema_merger_splitter_results_schema.json"
    output_schema_path = repo_root / "schema" / "schema_merger_splitter_output_schema.json"

    # 1. Extract configuration payloads
    output_filename = input_data["output_filename"]
    sources = input_data["sources"]

    # 2. Construct the Sovereign Container State
    container = MergerSplitterState(inputs=input_data)

    # 3. Build the Minimal Step Chain
    steps = [
        ExecuteMappingStep(sources, simulators_dir),
        WriteOutputStep(simulators_dir, output_filename, results_schema_path)
    ]

    # 4. Sequential loop execution for the domain data payload
    for step in steps:
        step.execute(container)

    # 5. GENERATE EXECUTION RECEIPT (Matches schema_merger_splitter_output_schema)
    # Construct the structural receipt matching the requirements
    execution_receipt = {
        "inputs": input_data,
        "results": {
            "success": container.success,
            "errors": getattr(container, "errors", [])
        }
    }

    # Validate our programmatic receipt output against the target output schema
    try:
        with output_schema_path.open("r", encoding="utf-8") as os_file:
            output_schema = json.load(os_file)
        validate(instance=execution_receipt, schema=output_schema)
        
        # Write the receipt file to disk for GitHub Actions tracking
        with execution_receipt_path.open("w", encoding="utf-8") as r_file:
            json.dump(execution_receipt, r_file, indent=2)
        logger.info(f"Execution receipt successfully persisted to {execution_receipt_path}")
    except Exception as receipt_err:
        logger.error(f"Failed to generate valid pipeline execution receipt: {receipt_err}")

    return container

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Missing input JSON configuration path.")
        sys.exit(1)

    input_file_path = Path(sys.argv[1]).resolve()
    repo_root = Path(__file__).resolve().parents[1]
    
    # Context Locations
    simulators_dir = input_file_path.parent
    execution_receipt_path = simulators_dir / "execution_receipt.json"

    # Load and validate configuration payload matching input schema rules
    try:
        with input_file_path.open("r", encoding="utf-8") as f:
            input_payload = json.load(f)
        
        input_schema_path = repo_root / "schema" / "schema_merger_splitter_input_schema.json"
        with input_schema_path.open("r", encoding="utf-8") as s_file:
            input_schema = json.load(s_file)
            
        validate(instance=input_payload, schema=input_schema)
        logger.info("Inbound configuration validated successfully.")
    except Exception as initialization_err:
        logger.critical(f"Inbound Schema Integrity Failure: {initialization_err}")
        sys.exit(1)

    # Execute complete operations
    final_view = run_pure_pipeline(input_payload, simulators_dir, execution_receipt_path)
    sys.exit(0 if final_view.success else 1)