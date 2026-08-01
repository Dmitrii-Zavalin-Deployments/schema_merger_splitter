import pytest

from src.state.merger_splitter_state import MergerSplitterState

# -----------------------------------------------------------------------------
# Test Narrative: MergerSplitterState Integrity
# -----------------------------------------------------------------------------
# These tests ensure the Sovereign Container state object maintains strict 
# type compliance and operational integrity for all properties.

# We instantiate the container to verify that the internal state correctly 
# initializes with the provided input payload and default values.
def test_state_initialization():
    # We define the initial input data for the state object.
    inputs = {"test": "data"}
    
    # We create the state container instance.
    state = MergerSplitterState(inputs=inputs)
    
    # We assert that the state correctly reflects the provided input and default baseline.
    assert state.inputs == inputs
    assert state.merged_output == {}
    assert state.success is False
    assert state.errors == []

# We verify the structural integrity of the merged_output setter.
# It must strictly reject non-dictionary inputs to prevent data corruption.
def test_merged_output_setter_type_error():
    # We instantiate a fresh state object.
    state = MergerSplitterState(inputs={})
    
    # We assert that attempting to assign a list instead of a dict raises the expected TypeError.
    with pytest.raises(TypeError, match="Merged output must be a dictionary."):
        state.merged_output = ["not", "a", "dictionary"]

# We validate that the mutable properties behave correctly when provided 
# with compliant data structures.
def test_property_setters():
    # We instantiate the state container.
    state = MergerSplitterState(inputs={})
    
    # We verify the setter functionality for merged_output.
    new_output = {"processed": True}
    state.merged_output = new_output
    assert state.merged_output == new_output
    
    # We verify that the success boolean flag updates correctly.
    state.success = True
    assert state.success is True
    
    # We verify that the error list accurately accepts and stores new entries.
    new_errors = ["Error 1", "Error 2"]
    state.errors = new_errors
    assert state.errors == new_errors