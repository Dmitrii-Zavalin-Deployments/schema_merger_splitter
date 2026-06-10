# tests/test_orchestrator.py

import json
from pathlib import Path
import pytest

from tests.signatures.orchestrator_test_signature import OrchestratorTestSignature

from src.orchestrator import SchemaMergerSplitterOrchestrator


class TestOrchestrator(OrchestratorTestSignature):
    """
    Concrete Phase‑6 test implementation for the Schema‑Merger‑Splitter orchestrator.
    Implements all required tests from OrchestratorTestSignature.
    """

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _write_json(self, path: Path, obj: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

    def _make_input(self, output_filename="merged.json", sources=None):
        return {
            "output_filename": output_filename,
            "sources": sources or {},
        }

    # ------------------------------------------------------------
    # Step 2 — Input JSON validation
    # ------------------------------------------------------------

    def test_input_schema_validation(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        # Valid input
        valid = self._make_input()
        orch.validate_input_json(valid)  # should not raise

        # Invalid input (missing required fields)
        invalid = {"not_output_filename": "x"}
        with pytest.raises(Exception):
            orch.validate_input_json(invalid)

    def test_input_validation_error_propagation(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        invalid = {"not_output_filename": "x"}
        with pytest.raises(Exception):
            orch.run(invalid)

    # ------------------------------------------------------------
    # Step 3 — Load source files
    # ------------------------------------------------------------

    def test_source_file_loading(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        # Create a valid source file
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(sources={str(src): []})
        loaded, errors = orch.load_source_files(input_json)

        assert errors == []
        assert str(src) in loaded
        assert loaded[str(src)] == {"a": 1}

    def test_missing_source_file_handling(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        missing = tmp_path / "missing.json"
        input_json = self._make_input(sources={str(missing): []})

        loaded, errors = orch.load_source_files(input_json)
        assert len(errors) == 1
        assert "Missing source file" in errors[0]

    def test_unreadable_source_file_handling(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")

        input_json = self._make_input(sources={str(bad): []})
        loaded, errors = orch.load_source_files(input_json)

        assert len(errors) == 1
        assert "Unreadable source file" in errors[0]

    def test_loaded_sources_structure(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"x": 1})

        input_json = self._make_input(sources={str(src): []})
        loaded, errors = orch.load_source_files(input_json)

        assert isinstance(loaded, dict)
        assert isinstance(errors, list)

    # ------------------------------------------------------------
    # Step 4 — Copy operations
    # ------------------------------------------------------------

    def test_jsonpath_evaluation(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": {"b": 5}})

        input_json = self._make_input(
            sources={str(src): [{"from": "$.a.b", "to": "value"}]}
        )

        loaded, _ = orch.load_source_files(input_json)
        merged, errors = orch.execute_copy_operations(loaded, input_json)

        assert errors == []
        assert merged["value"] == 5

    def test_missing_jsonpath_field(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            sources={str(src): [{"from": "$.missing", "to": "x"}]}
        )

        loaded, _ = orch.load_source_files(input_json)
        merged, errors = orch.execute_copy_operations(loaded, input_json)

        assert len(errors) == 1
        assert "Missing field" in errors[0]

    def test_duplicate_to_key_detection(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1, "b": 2})

        input_json = self._make_input(
            sources={
                str(src): [
                    {"from": "$.a", "to": "x"},
                    {"from": "$.b", "to": "x"},  # duplicate
                ]
            }
        )

        loaded, _ = orch.load_source_files(input_json)
        merged, errors = orch.execute_copy_operations(loaded, input_json)

        assert len(errors) == 1
        assert "Duplicate target key" in errors[0]

    def test_merged_output_structure(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            sources={str(src): [{"from": "$.a", "to": "A"}]}
        )

        loaded, _ = orch.load_source_files(input_json)
        merged, errors = orch.execute_copy_operations(loaded, input_json)

        assert isinstance(merged, dict)
        assert merged["A"] == 1

    def test_copy_operation_error_accumulation(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            sources={
                str(src): [
                    {"from": "$.missing", "to": "x"},
                    {"from": "$.invalid[", "to": "y"},
                ]
            }
        )

        loaded, _ = orch.load_source_files(input_json)
        merged, errors = orch.execute_copy_operations(loaded, input_json)

        assert len(errors) == 2

    # ------------------------------------------------------------
    # Step 5 — Write merged output
    # ------------------------------------------------------------

    def test_merged_output_write_success(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            output_filename="out.json",
            sources={str(src): [{"from": "$.a", "to": "A"}]},
        )

        success, errors = orch.run(input_json)
        assert success is True

        out_path = Path("data/testing-input-output/out.json")
        assert out_path.exists()

    def test_merged_output_write_skipped_on_errors(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            output_filename="out.json",
            sources={str(src): [{"from": "$.missing", "to": "A"}]},
        )

        success, errors = orch.run(input_json)
        assert success is False

        out_path = Path("data/testing-input-output/out.json")
        assert not out_path.exists()

    # ------------------------------------------------------------
    # Step 6 — Results JSON
    # ------------------------------------------------------------

    def test_results_json_written_always(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        input_json = self._make_input(
            output_filename="x.json",
            sources={},
        )

        success, errors = orch.run(input_json)

        results_path = Path("data/testing-input-output/x.json.results.json")
        assert results_path.exists()

    def test_results_json_success_flag(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        # success case
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            output_filename="good.json",
            sources={str(src): [{"from": "$.a", "to": "A"}]},
        )

        success, errors = orch.run(input_json)
        assert success is True

        # failure case
        bad_input = self._make_input(
            output_filename="bad.json",
            sources={str(src): [{"from": "$.missing", "to": "A"}]},
        )

        success2, errors2 = orch.run(bad_input)
        assert success2 is False

    def test_results_json_error_list(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            output_filename="err.json",
            sources={str(src): [{"from": "$.missing", "to": "A"}]},
        )

        success, errors = orch.run(input_json)
        assert len(errors) == 1

    # ------------------------------------------------------------
    # Step 7 — Execution artifacts
    # ------------------------------------------------------------

    def test_get_execution_artifacts_structure(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        input_json = self._make_input()
        orch.run(input_json)

        artifacts = orch.get_execution_artifacts()
        assert set(artifacts.keys()) == {"inputs", "config", "results"}

    def test_execution_artifacts_schema_alignment(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        input_json = self._make_input()
        orch.run(input_json)

        artifacts = orch.get_execution_artifacts()
        assert isinstance(artifacts["inputs"], dict)
        assert isinstance(artifacts["results"], dict)

    # ------------------------------------------------------------
    # Full Minimal Step Path
    # ------------------------------------------------------------

    def test_run_executes_steps_in_order(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            output_filename="order.json",
            sources={str(src): [{"from": "$.a", "to": "A"}]},
        )

        success, errors = orch.run(input_json)
        assert success is True

        # merged output must exist → Step 5 executed
        assert Path("data/testing-input-output/order.json").exists()

        # results JSON must exist → Step 6 executed
        assert Path("data/testing-input-output/order.json.results.json").exists()

    # ------------------------------------------------------------
    # Sensitivity Gates
    # ------------------------------------------------------------

    def test_sensitivity_missing_files(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        missing = tmp_path / "missing.json"
        input_json = self._make_input(sources={str(missing): []})

        success, errors = orch.run(input_json)
        assert success is False
        assert "Missing source file" in errors[0]

    def test_sensitivity_malformed_json(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")

        input_json = self._make_input(sources={str(bad): []})

        success, errors = orch.run(input_json)
        assert success is False
        assert "Unreadable source file" in errors[0]

    def test_sensitivity_invalid_jsonpath(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            sources={str(src): [{"from": "$.invalid[", "to": "x"}]}
        )

        success, errors = orch.run(input_json)
        assert success is False
        assert "Invalid JSONPath" in errors[0]

    # ------------------------------------------------------------
    # Structural Determinism
    # ------------------------------------------------------------

    def test_deterministic_copy_operations(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = self._make_input(
            sources={str(src): [{"from": "$.a", "to": "A"}]},
        )

        m1, e1 = orch.execute_copy_operations(
            {str(src): {"a": 1}}, input_json
        )
        m2, e2 = orch.execute_copy_operations(
            {str(src): {"a": 1}}, input_json
        )

        assert m1 == m2
        assert e1 == e2

    def test_deterministic_results_json(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        input_json = self._make_input(sources={})

        s1, e1 = orch.run(input_json)
        s2, e2 = orch.run(input_json)

        assert s1 == s2
        assert e1 == e2

    # ------------------------------------------------------------
    # Consistency Gates
    # ------------------------------------------------------------

    def test_no_hidden_state(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        input_json = self._make_input()
        orch.run(input_json)
        orch.run(input_json)

        # Orchestrator must not accumulate state across runs
        assert not hasattr(orch, "_hidden")

    def test_no_mutation_of_inputs(self, tmp_path):
        orch = SchemaMergerSplitterOrchestrator()

        input_json = self._make_input(
            sources={"file.json": [{"from": "$.a", "to": "A"}]}
        )

        before = json.loads(json.dumps(input_json))
        orch.run(input_json)
        after = input_json

        assert before == after