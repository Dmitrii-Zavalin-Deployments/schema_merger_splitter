import json
from pathlib import Path
from jsonschema import validate
from src.pipeline.pipeline_interface import PipelineInterface

class MergerSplitterState(PipelineInterface):
    """
    Sovereign Container: Aggregates the pure domain output state.
    Enforces a strict zero-default policy with no configuration tracking.
    """
    __slots__ = ["_merged_output", "_success", "_errors", "_base_dir"]

    def __init__(self):
        self._merged_output = {}
        self._success = False
        self._errors = []
        self._base_dir = Path(__file__).resolve().parents[2]

    @property
    def merged_output(self) -> dict:
        return self._merged_output

    @merged_output.setter
    def merged_output(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError("Merged output must be a dictionary.")
        self._merged_output = value

    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, value: bool):
        self._success = bool(value)

    @property
    def errors(self) -> list[str]:
        return self._errors

    @errors.setter
    def errors(self, value: list):
        self._errors = list(value)

    def validate_output_schema(self) -> None:
        """Validates the final assembled state against the output parity schema."""
        schema_path = self._base_dir / "schema" / "schema_merger_splitter_output_schema.json"
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        
        assembled = {
            "merged_output": self._merged_output,
            "metrics": {"success": self._success, "errors": self._errors}
        }
        validate(instance=assembled, schema=schema)