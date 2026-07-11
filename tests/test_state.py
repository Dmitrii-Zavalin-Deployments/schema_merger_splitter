import pytest
from src.state.merger_splitter_state import MergerSplitterState

# -----------------------------------------------------------------------------
# Test Narrative: MergerSplitterState Integrity
# -----------------------------------------------------------------------------
# These tests ensure the Sovereign Container state object maintains strict 
# type compliance and operational integrity for all properties.

def test_state_initialization():
    # [Scenario]: Verify initial state upon instantiation.
    inputs = {"test": "data"}
    state = MergerSplitterState(inputs=inputs)
    
    assert state.inputs == inputs
    assert state.merged_output == {}
    assert state.success is False
    assert state.errors == []

def test_merged_output_setter_type_error():
    # [Scenario: Line 29]: Verify that the setter raises a TypeError when 
    # provided with an invalid data structure (non-dict).
    state = MergerSplitterState(inputs={})
    
    with pytest.raises(TypeError, match="Merged output must be a dictionary."):
        state.merged_output = ["not", "a", "dictionary"]

def test_property_setters():
    # [Scenario]: Verify standard valid assignments for all mutable properties.
    state = MergerSplitterState(inputs={})
    
    # Test merged_output
    new_output = {"processed": True}
    state.merged_output = new_output
    assert state.merged_output == new_output
    
    # Test success
    state.success = True
    assert state.success is True
    
    # Test errors
    new_errors = ["Error 1", "Error 2"]
    state.errors = new_errors
    assert state.errors == new_errors