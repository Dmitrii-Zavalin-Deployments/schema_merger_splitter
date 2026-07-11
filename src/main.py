import sys
import json
import logging
from pathlib import Path
from jsonschema import validate
from src.state.merger_splitter_state import MergerSplitterState
from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from interfaces.step_interface import PipelineInterface

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("main")

def run_pure_pipeline(input_data: dict, project_base: Path) -> PipelineInterface:
    """
    Direct Orchestration Context: Constructs the Sovereign Container 
    and steps through the execution chain without configuration layers.
    """
    # 1. Enforce strict directory architecture alignment
    # FIXED: Updated path to match existing data directory structure
    simulators_dir = project_base / "data" / "testing-input-output"
    results_json_path = project_base / "schema" / "schema_merger_splitter_results_schema.json"

    # 2. Extract configuration payloads
    output_filename = input_data["output_filename"]
    sources = input_data["sources"]

    # 3. Construct the Sovereign Container
    container = MergerSplitterState(inputs=input_data)

    # 4. Build the Minimal Step Chain
    steps = [
        ExecuteMappingStep(sources, simulators_dir),
        WriteOutputStep(simulators_dir, output_filename, results_json_path)
    ]

    # 5. Sequential loop execution
    for step in steps:
        step.execute(container)

    return container

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Missing input JSON configuration path.")
        sys.exit(1)

    input_file_path = Path(sys.argv[1]).resolve()
    base_dir = Path(__file__).resolve().parents[1]

    # Load and validate configuration payload matching input schema rules
    try:
        with input_file_path.open("r", encoding="utf-8") as f:
            input_payload = json.load(f)
        
        input_schema_path = base_dir / "schema" / "schema_merger_splitter_input_schema.json"
        with input_schema_path.open("r", encoding="utf-8") as s_file:
            input_schema = json.load(s_file)
            
        validate(instance=input_payload, schema=input_schema)
        logger.info("Configuration validated successfully.")
    except Exception as initialization_err:
        logger.critical(f"Inbound Schema Integrity Failure: {initialization_err}")
        sys.exit(1)

    # Execute complete extraction mapping operations
    final_view = run_pure_pipeline(input_payload, base_dir)
    sys.exit(0 if final_view.success else 1)