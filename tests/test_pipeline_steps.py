import pytest
from unittest.mock import patch
from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from src.state.merger_splitter_state import MergerSplitterState

# -----------------------------------------------------------------------------
# Test Narrative: Pipeline Steps Structural Error-Handling Parity
# -----------------------------------------------------------------------------
# These tests verify the robustness of our pipeline steps. We force execution
# through various error conditions to ensure that the container state captures
# all failures appropriately, maintaining system stability.

# We test the scenario where a required source file is missing.
# The pipeline must gracefully record this error instead of raising a system exception.
def test_execute_mapping_missing_file(tmp_path):
    # We define a source path that points to a non-existent file.
    sources = {"non_existent.json": [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    # We execute the mapping step.
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # We assert that the step fails and records the specific error.
    assert container.success is False
    assert any("Missing source file" in err for err in container.errors)

# We ensure that syntactically malformed JSON files are intercepted.
# The parser must fail safely, registering an error in the container state.
def test_execute_mapping_unreadable_file(tmp_path):
    # We create a file with invalid JSON content.
    filename = "broken.json"
    broken_file = tmp_path / filename
    broken_file.write_text("{ broken raw formatting ...", encoding="utf-8")
    
    sources = {filename: [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # We verify the error is captured in the container.
    assert container.success is False
    assert any("Unreadable file" in err for err in container.errors)

# We validate the collision guard mechanism to prevent data loss.
# Two transformations writing to the same target key should be rejected.
def test_execute_mapping_duplicate_key(tmp_path):
    # We create a valid file with data.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10, "p2": 20}', encoding="utf-8")
    
    # We set up a source that maps two different fields to the same target key.
    sources = {
        filename: [
            {"from": "$.p1", "to": "collision_key"},
            {"from": "$.p2", "to": "collision_key"}
        ]
    }
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # We assert that the collision is detected and the container marks it as a failure.
    assert container.success is False
    assert any("Duplicate target key conflict" in err for err in container.errors)

# We check that the JSONPath expression engine handles syntax errors robustly.
# An unparseable path string must not crash the entire execution thread.
def test_execute_mapping_invalid_jsonpath(tmp_path):
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    # We define a source with a malformed JSONPath expression.
    sources = {filename: [{"from": "$.[invalid-syntax!!", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # We assert that the invalid path is caught and logged to the error list.
    assert container.success is False
    assert any("Invalid JSONPath" in err for err in container.errors)

# We verify the logic when JSONPath is valid, but the target key is missing.
# An empty result set is insufficient for downstream steps and must be a failure.
def test_execute_mapping_no_matches(tmp_path):
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    # We map to a field that doesn't exist in the input JSON.
    sources = {filename: [{"from": "$.non_existent_field", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    # We verify the failure state.
    assert container.success is False
    assert any("Field missing for path" in err for err in container.errors)

# We test the schema validation setup for writing outputs.
# The pipeline must throw a FileNotFoundError if the schema configuration file is missing.
def test_write_output_schema_not_found(tmp_path):
    container = MergerSplitterState(inputs={})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    # We simulate a missing schema file.
    with patch("src.pipeline.steps.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            step.execute(container)

# We handle the case where the schema file exists but cannot be read.
# This ensures that OS/IO errors are escalated correctly.
def test_write_output_schema_unreadable(tmp_path):
    container = MergerSplitterState(inputs={})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    # We simulate an error during file opening.
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open", side_effect=Exception("Disk Read Error")):
            with pytest.raises(Exception, match="Disk Read Error"):
                step.execute(container)

# We verify structural payload validation failure.
# Even if the file exists and is readable, the assembled payload must comply with the schema.
def test_write_output_validation_fails(tmp_path):
    # We instantiate the container with data that will trigger a schema mismatch.
    container = MergerSplitterState(inputs={"invalid_shape": True})
    container.success = True
    container.errors = []
    
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    # We simulate a failure in the validation step.
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open"):
            with patch("src.pipeline.steps.json.load", return_value={"type": "object"}):
                with patch("src.pipeline.steps.validate", side_effect=Exception("Validation Mismatch")):
                    with pytest.raises(Exception, match="Validation Mismatch"):
                        step.execute(container)

# We perform a final check on the happy path.
# This verifies that when everything is configured correctly, the pipeline executes the write operation.
def test_write_output_happy_path(tmp_path):
    # We set the container to a successful state with prepared data.
    container = MergerSplitterState(inputs={"test": "data"})
    container.success = True
    container.errors = []
    container.merged_output = {"p": 123}
    
    results_path = tmp_path / "results" / "receipt.json"
    step = WriteOutputStep(tmp_path, "output.json", results_path)
    
    # We simulate successful validation and verify that json.dump is called to output the file.
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open"):
            with patch("src.pipeline.steps.json.load", return_value={}):
                with patch("src.pipeline.steps.validate", return_value=True):
                    with patch("json.dump") as mock_dump:
                        step.execute(container)
                        assert mock_dump.called