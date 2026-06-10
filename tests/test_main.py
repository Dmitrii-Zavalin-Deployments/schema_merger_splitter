# tests/test_main.py
import json
import logging
from unittest.mock import patch, mock_open
from src.main import main

def test_main_no_active_runs(caplog):
    """
    Test Stage 1 Early Exit:
    If the controller evaluates the config and returns an empty run list,
    main.py should log a specific message and return before touching the Orchestrator.
    """
    with caplog.at_level(logging.INFO):
        with patch("src.main.SchemaMergerSplitterController") as MockController, \
             patch("pathlib.Path.open", mock_open(read_data='{"mocked": "config"}')):
             
            # Setup the mock controller to return an empty run list
            mock_controller_inst = MockController.return_value
            mock_controller_inst.load_and_evaluate_config.return_value = []
            
            # Execute
            main()
            
            # Verify the early exit log was triggered
            assert "No runs activated by config conditions." in caplog.text
            
            # Verify the controller was called correctly
            mock_controller_inst.load_and_evaluate_config.assert_called_once()
            # Verify it never tried to load an input file
            mock_controller_inst.load_input_file.assert_not_called()

def test_main_with_active_run_and_errors(caplog):
    """
    Test Stage 1 & Stage 2 Full Execution:
    Simulates a run being activated, loads data, runs the orchestrator (simulating an error 
    to hit the error-logging lines), and triggers the output assembler.
    """
    with caplog.at_level(logging.INFO):
        # Patch all external dependencies
        with patch("src.main.SchemaMergerSplitterController") as MockController, \
             patch("src.main.SchemaMergerSplitterOrchestrator") as MockOrchestrator, \
             patch("src.main.SchemaMergerSplitterOutputAssembler") as MockAssembler, \
             patch("pathlib.Path.open", mock_open(read_data='{"mocked": "config"}')):
             
            # 1. Setup Controller Mock
            mock_controller_inst = MockController.return_value
            # Return one run: (input_file, output_assembler_file)
            mock_controller_inst.load_and_evaluate_config.return_value = [("mock_in.json", "mock_out.json")]
            # Return the required output_filename and sources dictionary
            mock_controller_inst.load_input_file.return_value = ("merged.txt", {"sourceA": "destA"})
            
            # 2. Setup Orchestrator Mock
            mock_orchestrator_inst = MockOrchestrator.return_value
            # Simulate a run that finishes but generated an error (to cover lines 91-92)
            mock_orchestrator_inst.run.return_value = (False, ["Simulated pipeline error"])
            # Provide the execution artifacts expected by the Assembler
            mock_orchestrator_inst.get_execution_artifacts.return_value = {
                "inputs": {"output_filename": "merged.txt", "sources": {"sourceA": "destA"}},
                "config": {"mocked": "config"},
                "results": {"success": False, "errors": ["Simulated pipeline error"]}
            }
            
            # 3. Setup Assembler Mock
            mock_assembler_inst = MockAssembler.return_value
            
            # Execute
            main()
            
            # --- Assertions ---
            
            # Controller
            mock_controller_inst.load_and_evaluate_config.assert_called_once()
            mock_controller_inst.load_input_file.assert_called_once_with("mock_in.json")
            
            # Orchestrator
            # Verify the validated config was injected
            assert mock_orchestrator_inst._config == {"mocked": "config"}
            # Verify run was called with the exact format dictated by main.py
            mock_orchestrator_inst.run.assert_called_once_with({
                "output_filename": "merged.txt",
                "sources": {"sourceA": "destA"}
            })
            mock_orchestrator_inst.get_execution_artifacts.assert_called_once()
            
            # Assembler
            mock_assembler_inst.assemble_final_output.assert_called_once_with(
                {"output_filename": "merged.txt", "sources": {"sourceA": "destA"}},
                {"mocked": "config"},
                {"success": False, "errors": ["Simulated pipeline error"]},
                "mock_out.json"
            )
            
            # Verify Logging Output
            assert "=== Executing run ===" in caplog.text
            assert "Input file: mock_in.json" in caplog.text
            assert "Error: Simulated pipeline error" in caplog.text
            assert "Final assembled output written to: mock_out.json" in caplog.text