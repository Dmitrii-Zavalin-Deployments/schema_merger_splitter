from interfaces.pipeline_interfaces import PipelineInterface

# -----------------------------------------------------------------------------
# Test Narrative: PipelineInterface Protocol Contract
# -----------------------------------------------------------------------------
# The PipelineInterface ensures that any finalized state provides read-only
# access to critical diagnostic fields. We use @runtime_checkable to verify
# that our concrete implementation satisfies the protocol requirements.

class ConcreteState(PipelineInterface):
    """A dummy state container used for structural validation."""
    def __init__(self, inputs, output, success, errors):
        self._inputs = inputs
        self._merged_output = output
        self._success = success
        self._errors = errors

    @property
    def inputs(self) -> dict: return self._inputs

    @property
    def merged_output(self) -> dict: return self._merged_output

    @property
    def success(self) -> bool: return self._success

    @property
    def errors(self) -> list[str]: return self._errors

def test_protocol_contract():
    # We verify that a container fulfilling the contract is type-compatible.
    # This ensures no pipeline state ever reaches the exit gate without
    # meeting the required data shape.
    
    dummy_data = {"key": "value"}
    container = ConcreteState(
        inputs=dummy_data,
        output=dummy_data,
        success=True,
        errors=[]
    )
    
    # Asserting isinstance checks the Protocol satisfaction.
    assert isinstance(container, PipelineInterface), "State failed to satisfy PipelineInterface"
    assert container.success is True