import pytest
from unittest.mock import patch, mock_open
from src.output_assembler import SchemaMergerSplitterOutputAssembler

# ------------------------------------------------------------
# 1. Type Enforcement Error Paths (Lines 52, 54, 56)
# ------------------------------------------------------------

def test_assembler_inputs_not_dict():
    """Forces line 52: tests that inputs cannot be a string."""
    assembler = SchemaMergerSplitterOutputAssembler()
    with pytest.raises(ValueError, match="Final output assembly error: 'inputs' must be a dict."):
        assembler.assemble_final_output(
            inputs="not_a_dict_string", 
            config={}, 
            results={}, 
            output_assembler_file="out.json"
        )

def test_assembler_config_not_dict():
    """Forces line 54: tests that config cannot be a list."""
    assembler = SchemaMergerSplitterOutputAssembler()
    with pytest.raises(ValueError, match="Final output assembly error: 'config' must be a dict."):
        assembler.assemble_final_output(
            inputs={}, 
            config=["not", "a", "dict"], 
            results={}, 
            output_assembler_file="out.json"
        )

def test_assembler_results_not_dict():
    """Forces line 56: tests that results cannot be an integer."""
    assembler = SchemaMergerSplitterOutputAssembler()
    with pytest.raises(ValueError, match="Final output assembly error: 'results' must be a dict."):
        assembler.assemble_final_output(
            inputs={}, 
            config={}, 
            results=12345, 
            output_assembler_file="out.json"
        )

# ------------------------------------------------------------
# 2. Relative Path Normalization Branch (Line 84)
# ------------------------------------------------------------

@patch("src.output_assembler.validate")
@patch("src.output_assembler.json.load")
@patch("src.output_assembler.json.dump")
@patch("pathlib.Path.mkdir")
def test_assembler_relative_path_resolution(mock_mkdir, mock_json_dump, mock_json_load, mock_validate):
    """
    Forces line 84: passing a relative path string means is_absolute() 
    evaluates to False, forcing the assembler to prepend base_dir.
    """
    assembler = SchemaMergerSplitterOutputAssembler()
    
    # We use mock_open to completely bypass physical file reads/writes
    with patch("pathlib.Path.open", mock_open()):
        
        # Supplying a relative path "relative_dir/out.json" (no leading slash)
        assembler.assemble_final_output(
            inputs={}, 
            config={}, 
            results={}, 
            output_assembler_file="relative_dir/out.json"
        )
        
        # If the execution reaches this point without crashing, line 84 
        # correctly resolved the relative string into a concrete Path object.