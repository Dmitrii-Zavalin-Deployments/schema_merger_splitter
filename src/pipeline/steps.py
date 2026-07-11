import json
from pathlib import Path
from jsonpath_ng import parse as jsonpath_parse
from jsonschema import validate
from interfaces.step_interface import StepInterface
from src.state.merger_splitter_state import MergerSplitterState

class ExecuteMappingStep(StepInterface):
    """Atomic Step 1: Transforms source documents using direct parameters."""
    def __init__(self, sources: dict, simulators_dir: Path):
        self.sources = sources
        self.simulators_dir = simulators_dir

    def execute(self, container: MergerSplitterState) -> None:
        merged = {}
        errors = []
        
        for filename, rules in self.sources.items():
            path = self.simulators_dir / filename
            if not path.exists():
                errors.append(f"Missing source file: {filename}")
                continue
                
            try:
                with path.open("r", encoding="utf-8") as f:
                    src_json = json.load(f)
            except Exception as e:
                errors.append(f"Unreadable file '{filename}': {e}")
                continue

            for rule in rules:
                from_expr, to_key = rule["from"], rule["to"]
                if to_key in merged:
                    errors.append(f"Duplicate target key conflict: '{to_key}'")
                    continue
                    
                try:
                    expr = jsonpath_parse(from_expr)
                    matches = [m.value for m in expr.find(src_json)]
                except Exception as e:
                    errors.append(f"Invalid JSONPath '{from_expr}': {e}")
                    continue
                    
                if not matches:
                    errors.append(f"Field missing for path '{from_expr}' in '{filename}'")
                    continue
                    
                merged[to_key] = matches[0]

        container.merged_output = merged
        container.success = (len(errors) == 0)
        container.errors = errors


class WriteOutputStep(StepInterface):
    """Atomic Step 2: Enforces validation schemas and writes to disk."""
    def __init__(self, simulators_dir: Path, output_filename: str, results_path: Path):
        self.simulators_dir = simulators_dir
        self.output_filename = output_filename
        self.results_path = results_path

    def execute(self, container: MergerSplitterState) -> None:
        # Enforce schema validation matching output rules
        # Inline validation for debugging state payload
        schema_path = self.simulators_dir.parents[1] / "schema" / "schema_merger_splitter_output_schema.json"
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        
        assembled = {"inputs": container.inputs, "results": {"success": container.success, "errors": container.errors}}
        try:
            validate(instance=assembled, schema=schema)
        except Exception as e:
            print(f"DEBUG: Schema Validation Failed: {e}")
            raise

        # Persist data payload if the operations succeeded completely
        if container.success:
            output_path = self.simulators_dir / self.output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(container.merged_output, f, indent=2)

        # Always write output execution metrics matching schema requirements
        results_payload = {
            "success": container.success,
            "errors": container.errors
        }
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        with self.results_path.open("w", encoding="utf-8") as f:
            json.dump(results_payload, f, indent=2)