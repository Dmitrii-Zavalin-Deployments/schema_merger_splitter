import pytest
from unittest.mock import patch, MagicMock
from src.main import run_pure_pipeline, main

def test_run_pure_pipeline_receipt_failure(tmp_path):
    input_data = {
        "sources": {"in.json": [{"from": "$.a", "to": "b"}]}
    }
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    invalid_receipt_path = simulators_dir / "receipt.json"
    
    with patch("src.main.validate", side_effect=Exception("Schema Invalid")):
        container = run_pure_pipeline(input_data, simulators_dir, "test_output.json", invalid_receipt_path)
    
    assert container is not None

def test_run_pure_pipeline_happy_path(tmp_path):
    input_data = {
        "sources": {"in.json": [{"from": "$.a", "to": "b"}]}
    }
    simulators_dir = tmp_path
    (simulators_dir / "in.json").write_text('{"a": 1}')
    receipt_path = simulators_dir / "receipt.json"
    
    container = run_pure_pipeline(input_data, simulators_dir, "test_output.json", receipt_path)
    
    assert receipt_path.exists()
    assert container.success is True

def test_main_missing_arguments():
    with patch("sys.argv", ["src/main.py"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_parse_args_exception():
    """Targets lines 81-82 by simulating an unexpected explosion during parsing."""
    with patch("argparse.ArgumentParser.parse_args", side_effect=RuntimeError("Forced parsing explosion")):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_integrity_failure(tmp_path):
    bad_config = tmp_path / "corrupted_config.json"
    bad_config.write_text("{ unparseable raw payload ...", encoding="utf-8")
    
    with patch("sys.argv", [
        "src/main.py", 
        "--input_output_folder", str(tmp_path), 
        "--input_file_name", "corrupted_config.json", 
        "--output_file_name", "out.json"
    ]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_execution_success(tmp_path):
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"sources": {}}', encoding="utf-8")
    
    mock_container = MagicMock()
    mock_container.success = True
    
    with patch("sys.argv", [
        "src/main.py", 
        "--input_output_folder", str(tmp_path), 
        "--input_file_name", "valid_config.json", 
        "--output_file_name", "out.json"
    ]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 0

def test_main_execution_pipeline_failure(tmp_path):
    valid_config = tmp_path / "valid_config.json"
    valid_config.write_text('{"sources": {}}', encoding="utf-8")
    
    mock_container = MagicMock()
    mock_container.success = False
    
    with patch("sys.argv", [
        "src/main.py", 
        "--input_output_folder", str(tmp_path), 
        "--input_file_name", "valid_config.json", 
        "--output_file_name", "out.json"
    ]):
        with patch("src.main.Path.open"):
            with patch("json.load", return_value={"sources": {}}):
                with patch("src.main.validate", return_value=True):
                    with patch("src.main.run_pure_pipeline", return_value=mock_container):
                        with pytest.raises(SystemExit) as exc_info:
                            main()
                        assert exc_info.value.code == 1