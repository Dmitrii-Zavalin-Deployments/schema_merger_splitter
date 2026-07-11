import json
from pathlib import Path
from jsonpath_ng import parse as jsonpath_parse
from src.state.merger_splitter_state import MergerSplitterState

class StepInterface:
    """Contract governance; bars speculative runtime modifications."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "execute" not in cls.__dict__ and not any("execute" in base.__dict__ for base in cls.__bases__):
            raise TypeError("CONSTITUTION VIOLATION: Subclasses must implement 'execute'.")
        
        for name in cls.__dict__:
            if not name.startswith("__") and name != "execute":
                raise TypeError(f"CONSTITUTION VIOLATION: '{name}' is a forbidden member.")

    def execute(self, container: MergerSplitterState) -> None:
        raise NotImplementedError


class ExecuteMappingStep(StepInterface):
    """Atomic Step 1: Transforms source documents using direct parameters."""
    def __init__(self, mappings: dict, source_dir: Path):
        self.mappings = mappings
        self.source_dir = source_dir

    def execute(self, container: MergerSplitterState) -> None:
        merged = {}
        errors = []
        
        for filename, rules in self.mappings.items():
            path = self.source_dir / filename
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
    def __init__(self, output_path: Path, metrics_path: Path):
        self.output_path = output_path
        self.metrics_path = metrics_path

    def execute(self, container: MergerSplitterState) -> None:
        # 1. Structural validation check across the state boundaries
        container.validate_output_schema()

        # 2. Persist domain data on success
        if container.success:
            with self.output_path.open("w", encoding="utf-8") as f:
                json.dump(container.merged_output, f, indent=2)

        # 3. Always persist runtime status metrics
        metrics = {"success": container.success, "errors": container.errors}
        with self.metrics_path.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)