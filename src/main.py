from pathlib import Path
from src.state.merger_splitter_state import MergerSplitterState
from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from src.pipeline.pipeline_interface import PipelineInterface

def run_pure_pipeline(mappings: dict, source_dir: Path, target_dir: Path) -> PipelineInterface:
    """
    Direct Orchestration Context: Constructs the Sovereign Container 
    and steps through the execution chain without any configuration layer.
    """
    # 1. Construct the Sovereign Container
    container = MergerSplitterState()

    # 2. Define concrete paths derived from direct arguments
    output_json = target_dir / "compiled_output.json"
    metrics_json = target_dir / "execution_metrics.json"

    # 3. Build the Minimal Step Chain
    steps = [
        ExecuteMappingStep(mappings, source_dir),
        WriteOutputStep(output_json, metrics_json)
    ]

    # 4. Sequential loop execution
    for step in steps:
        step.execute(container)

    # 5. Return the read-only Exit Gate interface
    return container

if __name__ == "__main__":
    # Example of direct, zero-config domain execution invocation
    BASE = Path(__file__).resolve().parents[1]
    
    EXPLICIT_MAPPINGS = {
        "sensor_data.json": [{"from": "$.payload.temperature", "to": "env_temp"}],
        "metadata.json":    [{"from": "$.system.identity_id", "to": "node_id"}]
    }
    
    final_view = run_pure_pipeline(
        mappings=EXPLICIT_MAPPINGS,
        source_dir=BASE / "data" / "testing-input-output",
        target_dir=BASE / "data" / "testing-input-output"
    )
    
    print(f"Pipeline Completed via Exit Gate. State Success: {final_view.success}")