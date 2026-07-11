from pathlib import Path
from interfaces.pipeline_interfaces import PipelineInterface

class MergerSplitterState(PipelineInterface):
    """
    Sovereign Container: Aggregates the pure domain output state.
    Enforces a strict zero-default policy with no external configuration tracking.
    """
    __slots__ = ["_inputs", "_merged_output", "_success", "_errors", "_base_dir"]

    def __init__(self, inputs: dict):
        self._inputs = inputs
        self._merged_output = {}
        self._success = False
        self._errors = []
        self._base_dir = Path(__file__).resolve().parents[2]

    @property
    def inputs(self) -> dict:
        return self._inputs

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

