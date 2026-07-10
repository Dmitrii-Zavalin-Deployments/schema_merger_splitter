from typing import Protocol

class StepInterface:
    """
    Contract-only interface for pipeline steps.
    Enforces a strict execution paradigm and prohibits unauthorized runtime members.
    """
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ALLOWED_MEMBERS = {"execute"} 
        for name in cls.__dict__:
            # Allows dunder methods like __init__ while blocking custom public/private methods
            if not name.startswith("__") and name not in ALLOWED_MEMBERS:
                raise TypeError(f"CONSTITUTION VIOLATION: '{name}' is forbidden.")

    def execute(self, container) -> None:
        """Transformation signature of the step."""
        raise NotImplementedError


class PipelineInterface(Protocol):
    """
    Composite, read-only view of the finalized state.
    Acts as the explicit exit gate for the module.
    
    Zero-Config Blueprint: Exposes pure domain processing attributes 
    and entirely omits configuration management overhead.
    """

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