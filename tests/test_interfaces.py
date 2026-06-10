import pytest
from src.interfaces.controller_interface import SchemaMergerSplitterControllerInterface
from src.interfaces.orchestrator_interface import SchemaMergerSplitterOrchestratorInterface
from src.interfaces.output_assembler_interface import SchemaMergerSplitterOutputAssemblerInterface

# --- 1. Controller Interface Tests ---

def test_controller_interface_enforcement():
    # Class that inherits but does NOT implement methods (forces base call)
    class PartialController(SchemaMergerSplitterControllerInterface):
        pass
    
    instance = PartialController()
    
    # Test NotImplementedError
    with pytest.raises(NotImplementedError):
        instance.load_and_evaluate_config("path")
    with pytest.raises(NotImplementedError):
        instance.load_input_file("path")

    # Test illegal member enforcement (from __init_subclass__)
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidController(SchemaMergerSplitterControllerInterface):
            def rogue_method(self): pass

# --- 2. Orchestrator Interface Tests ---

def test_orchestrator_interface_enforcement():
    class PartialOrchestrator(SchemaMergerSplitterOrchestratorInterface):
        pass

    instance = PartialOrchestrator()
    
    # All these calls will hit the base class NotImplementedError
    with pytest.raises(NotImplementedError):
        instance.run({})
    with pytest.raises(NotImplementedError):
        instance.validate_input_json({})
    with pytest.raises(NotImplementedError):
        instance.load_source_files({})
    with pytest.raises(NotImplementedError):
        instance.execute_copy_operations({}, {})
    with pytest.raises(NotImplementedError):
        instance.write_merged_output({}, {})
    with pytest.raises(NotImplementedError):
        instance.write_results_json(True, [], {})
    with pytest.raises(NotImplementedError):
        instance.get_execution_artifacts()

    # Test illegal member
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidOrchestrator(SchemaMergerSplitterOrchestratorInterface):
            def rogue_method(self): pass

# --- 3. Output Assembler Interface Tests ---

def test_output_assembler_interface_enforcement():
    class PartialAssembler(SchemaMergerSplitterOutputAssemblerInterface):
        pass
    
    instance = PartialAssembler()
    
    # Test NotImplementedError
    with pytest.raises(NotImplementedError):
        instance.assemble_final_output({}, {}, {}, "file")
    
    # Test illegal member
    with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
        class InvalidAssembler(SchemaMergerSplitterOutputAssemblerInterface):
            def bad_method(self): pass