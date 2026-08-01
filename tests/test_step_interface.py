import pytest

from interfaces.pipeline_interfaces import StepInterface

# -----------------------------------------------------------------------------
# Test Narrative: StepInterface Constitutional Enforcement
# -----------------------------------------------------------------------------
# We define the StepInterface as the foundational base for all computational steps.
# To prevent structural drift, any addition of unauthorized class members must 
# trigger an immediate TypeError during class definition.

class ValidStep(StepInterface):
    """A compliant implementation of the StepInterface."""
    def execute(self, container) -> None:
        pass

def test_constitution_violation():
    # We attempt to define a class with an unauthorized member 'rogue_attribute'.
    # This should trigger the __init_subclass__ check and raise a TypeError.
    
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class ForbiddenStep(StepInterface):
            rogue_attribute = "This should not exist"
            
            def execute(self, container) -> None:
                pass

def test_execution_signature():
    # We verify that a valid implementation maintains the required signature.
    # The execute method must accept a container and return None.
    
    step = ValidStep()
    step.execute(container=None)
