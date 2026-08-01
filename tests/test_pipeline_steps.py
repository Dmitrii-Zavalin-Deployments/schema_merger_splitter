from unittest.mock import patch

import pytest

from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from src.state.merger_splitter_state import MergerSplitterState

# =============================================================================
# DATA INTEGRATION TRACK: ExecuteMappingStep
# This section verifies the step responsible for scanning, extracting, 
# and mapping structural payloads across physical workspace files.
# =============================================================================

def test_execute_mapping_missing_file(tmp_path):
    # Setup: Define a mapping rule targetting a file that does not exist on disk.
    sources = {"non_existent.json": [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    # Execution: Trigger processing across the empty workspace directory.
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # Assertions: Verify isolation boundaries flag a clean recovery failure 
    # and append the missing file error to the tracking array.
    assert container.success is False
    assert any("Missing source file" in err for err in container.errors)


def test_execute_mapping_unreadable_file(tmp_path):
    # Setup: Create a file with corrupted, unparseable raw content.
    filename = "broken.json"
    broken_file = tmp_path / filename
    broken_file.write_text("{ broken raw formatting ...", encoding="utf-8")
    
    sources = {filename: [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    # Execution: Trigger step interpretation against the unparseable payload.
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # Assertions: The state must record a failure flag and capture the 
    # file structure corruption explicitly in its tracking state.
    assert container.success is False
    assert any("Unreadable file" in err for err in container.errors)


def test_execute_mapping_duplicate_key(tmp_path):
    # Setup: Create a perfectly valid file containing distinct origin fields.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10, "p2": 20}', encoding="utf-8")
    
    # Instruct the system to map two distinct sources into the same output field.
    sources = {
        filename: [
            {"from": "$.p1", "to": "collision_key"},
            {"from": "$.p2", "to": "collision_key"}
        ]
    }
    container = MergerSplitterState(inputs={"sources": sources})
    
    # Execution: Process the overlapping extraction rules sequentially.
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # Assertions: Ensure that implicit value overwrites are caught as 
    # data collision violations, marking the pipeline run as a failure.
    assert container.success is False
    assert any("Duplicate target key conflict" in err for err in container.errors)


def test_execute_mapping_invalid_jsonpath(tmp_path):
    # Setup: Create a valid JSON file to isolate path syntax parsing errors.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    # Provide a clearly malformed JSONPath syntax expression rule.
    sources = {filename: [{"from": "$.[invalid-syntax!!", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    # Execution: Attempt compilation and application of the invalid path syntax.
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # Assertions: Confirm syntax exceptions are caught cleanly within 
    # the orchestration loop instead of crashing the process thread.
    assert container.success is False
    assert any("Invalid JSONPath" in err for err in container.errors)


def test_execute_mapping_no_matches(tmp_path):
    # Setup: Instantiate a standard source data file structure.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    # Request a valid syntax field lookup for a key path that does not exist.
    sources = {filename: [{"from": "$.non_existent_field", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    # Execution: Perform the query lookup.
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # Assertions: Empty evaluation sets violate data presence boundaries, 
    # requiring explicit tracking inside the state container failures.
    assert container.success is False
    assert any("Field missing for path" in err for err in container.errors)


# =============================================================================
# PERSISTENCE TRACK: WriteOutputStep
# This section verifies disk output serializations, structural verification,
# and system error responses when structural definitions break down.
# =============================================================================

def test_write_output_schema_not_found(tmp_path):
    # Setup: Prepare an isolated execution step pointing at an invalid results schema.
    container = MergerSplitterState(inputs={"sources": {}})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    # Execution & Assertion: If the structural reference path is physically 
    # missing, the system must bubble up a standard FileNotFoundError.
    with patch("src.pipeline.steps.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            step.execute(container)


def test_write_output_schema_unreadable(tmp_path):
    # Setup: Prepare context targeting a valid location path layout.
    container = MergerSplitterState(inputs={"sources": {}})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    # Execution & Assertion: Force a low-level physical disk read crash 
    # when opening the verification schema file. The process must raise it immediately.
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open", side_effect=Exception("Disk Read Error")):
            with pytest.raises(Exception, match="Disk Read Error"):
                step.execute(container)


def test_write_output_validation_fails(tmp_path):
    # Setup: Create a container state containing an irregular payload shape.
    container = MergerSplitterState(inputs={"invalid_shape": True})
    container.success = True
    container.errors = []
    
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    # Execution & Assertion: Stub external validation engines to throw 
    # mismatched schema validations, testing defensive formatting checkpoints.
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open"):
            with patch("src.pipeline.steps.json.load", return_value={"type": "object"}):
                with patch("src.pipeline.steps.validate", side_effect=Exception("Validation Mismatch")):
                    with pytest.raises(Exception, match="Validation Mismatch"):
                        step.execute(container)


def test_write_output_happy_path(tmp_path):
    # Setup: Formulate a standard successful processing data layout profile.
    container = MergerSplitterState(inputs={"sources": {}})
    container.success = True
    container.errors = []
    container.merged_output = {"p": 123}
    
    results_path = tmp_path / "results" / "receipt.json"
    step = WriteOutputStep(tmp_path, "output.json", results_path)
    
    # Execution: Simulate normal filesystem conditions with correct parameters.
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open"):
            with patch("src.pipeline.steps.json.load", return_value={}):
                with patch("src.pipeline.steps.validate", return_value=True):
                    with patch("json.dump") as mock_dump:
                        step.execute(container)
                        # Assert that serialization execution completed cleanly.
                        assert mock_dump.called