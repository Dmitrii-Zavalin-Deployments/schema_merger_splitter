import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from src.state.merger_splitter_state import MergerSplitterState

# -----------------------------------------------------------------------------
# Test Narrative: Pipeline Steps Structural Error-Handling Parity
# -----------------------------------------------------------------------------
# These tests explicitly force execution through every defensive error branch 
# in src/pipeline/steps.py to guarantee 100% code path coverage and design safety.

def test_execute_mapping_missing_file(tmp_path):
    # [Scenario: Line 25-27] A declared source input file does not exist on disk.
    # The system must append an error to the container state and continue cleanly.
    sources = {"non_existent.json": [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Missing source file" in err for err in container.errors)


def test_execute_mapping_unreadable_file(tmp_path):
    # [Scenario: Line 32-35] A file exists but contains syntactically invalid JSON.
    # The parser failure must be intercepted cleanly, registering a state error.
    filename = "broken.json"
    broken_file = tmp_path / filename
    broken_file.write_text("{ broken raw formatting ...", encoding="utf-8")
    
    sources = {filename: [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Unreadable file" in err for err in container.errors)


def test_execute_mapping_duplicate_key(tmp_path):
    # [Scenario: Line 40-42] Multiple transformations attempt to write to the same target key.
    # To prevent destructive mutation overwrites, collision guards must catch this state.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10, "p2": 20}', encoding="utf-8")
    
    sources = {
        filename: [
            {"from": "$.p1", "to": "collision_key"},
            {"from": "$.p2", "to": "collision_key"}
        ]
    }
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Duplicate target key conflict" in err for err in container.errors)


def test_execute_mapping_invalid_jsonpath(tmp_path):
    # [Scenario: Line 47-50] The JSONPath rule contains unparseable syntax expressions.
    # The expression engine failure must be trapped without dropping the program runtime.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    sources = {filename: [{"from": "$.[invalid-syntax!!", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Invalid JSONPath" in err for err in container.errors)


def test_execute_mapping_no_matches(tmp_path):
    # [Scenario: Line 53-55] The JSONPath syntax is correct, but maps to a key missing from the file.
    # Empty match sets cannot satisfy data downstream; this counts as an operational failure.
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    sources = {filename: [{"from": "$.non_existent_field", "to": "p"}]}
    container = MergerSplitterState(inputs={"output_filename": "out.json", "sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Field missing for path" in err for err in container.errors)


def test_write_output_schema_not_found(tmp_path):
    # [Scenario: Line 78-79] The schema structural contract configuration file cannot be found.
    # A structural FileNotFoundError must be thrown immediately to avoid unchecked execution.
    container = MergerSplitterState(inputs={})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    with patch("src.pipeline.steps.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            step.execute(container)


def test_write_output_schema_unreadable(tmp_path):
    # [Scenario: Line 84-86] The file lookup handles the path, but the schema file contents are unparseable.
    # A critical log emission and a raw exception escalation must follow immediately.
    container = MergerSplitterState(inputs={})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open", side_effect=Exception("Disk Read Error")):
            with pytest.raises(Exception, match="Disk Read Error"):
                step.execute(container)


def test_write_output_validation_fails(tmp_path):
    # [Scenario: Line 92-94] The structural schema exists but the final assembled payload composition rules fail.
    # A validation mismatch error must trigger an exception to intercept bad downstream data drops.
    container = MergerSplitterState(inputs={})
    container.inputs = {"invalid_shape": True}
    container.success = True
    container.errors = []
    
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open"):
            with patch("src.pipeline.steps.json.load", return_value={"type": "object"}):
                with patch("src.pipeline.steps.validate", side_effect=Exception("Validation Mismatch")):
                    with pytest.raises(Exception, match="Validation Mismatch"):
                        step.execute(container)


def test_write_output_happy_path(tmp_path):
    # [Scenario: Happy Path Branch Fulfillment] Verifies clean file outputs are correctly
    # written when the container context signals completion without outstanding errors.
    container = MergerSplitterState(inputs={"test": "data"})
    container.success = True
    container.errors = []
    container.merged_output = {"p": 123}
    
    results_path = tmp_path / "results" / "receipt.json"
    step = WriteOutputStep(tmp_path, "output.json", results_path)
    
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open"):
            with patch("src.pipeline.steps.json.load", return_value={}):
                with patch("src.pipeline.steps.validate", return_value=True):
                    with patch("json.dump") as mock_dump:
                        step.execute(container)
                        assert mock_dump.called