import pytest
from unittest.mock import patch
from src.pipeline.steps import ExecuteMappingStep, WriteOutputStep
from src.state.merger_splitter_state import MergerSplitterState

def test_execute_mapping_missing_file(tmp_path):
    sources = {"non_existent.json": [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Missing source file" in err for err in container.errors)

def test_execute_mapping_unreadable_file(tmp_path):
    filename = "broken.json"
    broken_file = tmp_path / filename
    broken_file.write_text("{ broken raw formatting ...", encoding="utf-8")
    
    sources = {filename: [{"from": "$.p1", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Unreadable file" in err for err in container.errors)

def test_execute_mapping_duplicate_key(tmp_path):
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10, "p2": 20}', encoding="utf-8")
    
    sources = {
        filename: [
            {"from": "$.p1", "to": "collision_key"},
            {"from": "$.p2", "to": "collision_key"}
        ]
    }
    container = MergerSplitterState(inputs={"sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Duplicate target key conflict" in err for err in container.errors)

def test_execute_mapping_invalid_jsonpath(tmp_path):
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    sources = {filename: [{"from": "$.[invalid-syntax!!", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Invalid JSONPath" in err for err in container.errors)

def test_execute_mapping_no_matches(tmp_path):
    filename = "valid.json"
    valid_file = tmp_path / filename
    valid_file.write_text('{"p1": 10}', encoding="utf-8")
    
    sources = {filename: [{"from": "$.non_existent_field", "to": "p"}]}
    container = MergerSplitterState(inputs={"sources": sources})
    
    step = ExecuteMappingStep(sources, tmp_path)
    step.execute(container)
    
    assert container.success is False
    assert any("Field missing for path" in err for err in container.errors)

def test_write_output_schema_not_found(tmp_path):
    container = MergerSplitterState(inputs={"sources": {}})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    with patch("src.pipeline.steps.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            step.execute(container)

def test_write_output_schema_unreadable(tmp_path):
    container = MergerSplitterState(inputs={"sources": {}})
    step = WriteOutputStep(tmp_path, "out.json", tmp_path / "res.json")
    
    with patch("src.pipeline.steps.Path.exists", return_value=True):
        with patch("src.pipeline.steps.Path.open", side_effect=Exception("Disk Read Error")):
            with pytest.raises(Exception, match="Disk Read Error"):
                step.execute(container)

def test_write_output_validation_fails(tmp_path):
    container = MergerSplitterState(inputs={"invalid_shape": True})
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
    container = MergerSplitterState(inputs={"sources": {}})
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