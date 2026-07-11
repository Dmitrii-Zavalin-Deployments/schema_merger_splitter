from typing import Protocol, runtime_checkable

class StepInterface:
    """
    Contract-only interface for pipeline steps.
    Enforces a strict execution paradigm and prohibits unauthorized runtime members.
    """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ALLOWED_MEMBERS = {"execute"} 
        for name in cls.__dict__:
            if not name.startswith("__") and name not in ALLOWED_MEMBERS:
                raise TypeError(f"CONSTITUTION VIOLATION: '{name}' is forbidden.")

    def execute(self, container) -> None:
        """Transformation signature of the step."""
        raise NotImplementedError


@runtime_checkable
class PipelineInterface(Protocol):
    """
    Composite, read-only view of the finalized state.
    Acts as the explicit exit gate for the module.
    """

    @property
    def inputs(self) -> dict:
        """Access to the original source mapping configuration input."""
        ...

    @property
    def merged_output(self) -> dict:
        """Access to the finalized merged payload dictionary."""
        ...

    @property
    def success(self) -> bool:
        """Access to the final execution status flag."""
        ...

    @property
    def errors(self) -> list[str]:
        """Access to the collection of runtime validation errors."""
        ...