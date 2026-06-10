import pytest
from src.interfaces.controller_interface import SchemaMergerSplitterControllerInterface
from src.interfaces.orchestrator_interface import SchemaMergerSplitterOrchestratorInterface
from src.interfaces.output_assembler_interface import SchemaMergerSplitterOutputAssemblerInterface

# --- 1. Controller Interface Tests ---

def test_controller_interface_enforcement():
    # Test that valid subclass is allowed
    class ValidController(SchemaMergerSplitterControllerInterface):
        def load_and_evaluate_config(self, config_path): pass
        def load_input_file(self, input_file_path): pass
    
    ValidController() # Should not raise

    # Test that illegal member raises TypeError [cite: 3]
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidController(SchemaMergerSplitterControllerInterface):
            def unauthorized_method(self): pass
    
    # Test NotImplementedError [cite: 7, 8]
    c = ValidController()
    with pytest.raises(NotImplementedError):
        c.load_and_evaluate_config("path")
    with pytest.raises(NotImplementedError):
        c.load_input_file("path")

# --- 2. Orchestrator Interface Tests ---

def test_orchestrator_interface_enforcement():
    class ValidOrchestrator(SchemaMergerSplitterOrchestratorInterface):
        def run(self, input_json_instance): pass
        def validate_input_json(self, input_json_instance): pass
        def load_source_files(self, input_json_instance): pass
        def execute_copy_operations(self, loaded_sources, input_json_instance): pass
        def write_merged_output(self, merged_output, input_json_instance): pass
        def write_results_json(self, success, errors, input_json_instance): pass
        def get_execution_artifacts(self): pass

    # Test illegal member [cite: 19]
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidOrchestrator(SchemaMergerSplitterOrchestratorInterface):
            def rogue_method(self): pass

    # Test NotImplementedError [cite: 20-28]
    o = ValidOrchestrator()
    with pytest.raises(NotImplementedError):
        o.run({})
    with pytest.raises(NotImplementedError):
        o.validate_input_json({})
    with pytest.raises(NotImplementedError):
        o.load_source_files({})
    with pytest.raises(NotImplementedError):
        o.execute_copy_operations({}, {})
    with pytest.raises(NotImplementedError):
        o.write_merged_output({}, {})
    with pytest.raises(NotImplementedError):
        o.write_results_json(True, [], {})
    with pytest.raises(NotImplementedError):
        o.get_execution_artifacts()

# --- 3. Output Assembler Interface Tests ---

def test_output_assembler_interface_enforcement():
    class ValidAssembler(SchemaMergerSplitterOutputAssemblerInterface):
        def assemble_final_output(self, inputs, config, results, output_assembler_file): pass
    
    # Test illegal member [cite: 11]
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidAssembler(SchemaMergerSplitterOutputAssemblerInterface):
            def bad_method(self): pass
            
    # Test NotImplementedError [cite: 14]
    a = ValidAssembler()
    with pytest.raises(NotImplementedError):
        a.assemble_final_output({}, {}, {}, "file")