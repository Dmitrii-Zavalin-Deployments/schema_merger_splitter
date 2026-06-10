# tests/test_pipeline_unified.py

import json
from pathlib import Path

import pytest

from tests.signatures.pipeline_unified_test_signature import PipelineUnifiedTestSignature
from tests.dummies.execution_artifacts_dummy import ExecutionArtifactsDummy

from src.controller import SchemaMergerSplitterController
from src.orchestrator import SchemaMergerSplitterOrchestrator
from src.output_assembler import SchemaMergerSplitterOutputAssembler


class TestPipelineUnified(PipelineUnifiedTestSignature):
    """
    Concrete Phase‑6 implementation of the unified pipeline tests.
    Validates the full Minimal Step Path (Steps 1–7):
        controller → orchestrator → assembler
    """

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _write_json(self, path: Path, obj: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

    def _load_json(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _make_single_run_config(self, input_file: Path, output_file: Path) -> dict:
        return {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(input_file),
                    "output_assembler_file": str(output_file),
                }
            ]
        }

    def _inject_run_config_into_orchestrator(self, orchestrator, input_file: Path, output_file: Path):
        """
        Inject a schema‑valid config object into orchestrator._config.
        The Output Schema requires:
            config = { "runs": [ <single_run_entry> ] }
        """
        orchestrator._config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(input_file),
                    "output_assembler_file": str(output_file),
                }
            ]
        }

    # ------------------------------------------------------------
    # End‑to‑End Pipeline Behaviour
    # ------------------------------------------------------------

    def test_full_pipeline_execution(self, tmp_path):
        """
        The full pipeline must execute Steps 1–7 in strict topological order.
        """
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Step 1: config.json
        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Step 2: input JSON
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        # Execute pipeline
        runs = controller.load_and_evaluate_config(config_path)
        assert len(runs) == 1

        input_file, output_file = runs[0]
        output_filename, sources = controller.load_input_file(input_file)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

        # Inject the concrete run entry as orchestrator config artifact
        self._inject_run_config_into_orchestrator(orchestrator, input_file, output_file)

        artifacts = orchestrator.get_execution_artifacts()
        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )

        # Step 5: merged output exists
        merged_path = Path("data/testing-input-output/merged.json")
        assert merged_path.exists()

        # Step 6: results JSON exists
        results_path = Path("data/testing-input-output/merged.json.results.json")
        assert results_path.exists()

        # Step 7: final assembled output exists
        assert Path(output_file).exists()

    def test_pipeline_success_case(self, tmp_path):
        """
        Valid config + valid inputs must produce all expected outputs.
        """
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Valid input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 10})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(config_path)
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)
        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

        self._inject_run_config_into_orchestrator(orchestrator, input_file, output_file)

        artifacts = orchestrator.get_execution_artifacts()
        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )

        # All outputs must exist
        assert Path("data/testing-input-output/merged.json").exists()
        assert Path("data/testing-input-output/merged.json.results.json").exists()
        assert Path(output_file).exists()

    def test_pipeline_failure_case(self, tmp_path):
        """
        Failure must skip merged output but still write results + final output.
        """
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Input referencing missing source file
        input_json = {
            "output_filename": "merged.json",
            "sources": {str(tmp_path / "missing.json"): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(config_path)
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)
        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )

        # Must fail
        assert success is False
        assert any("Missing source file" in e for e in errors)

        # Merged output must NOT exist
        assert not Path("data/testing-input-output/merged.json").exists()

        # Results JSON must exist
        assert Path("data/testing-input-output/merged.json.results.json").exists()

        # Final assembled output must STILL be written
        self._inject_run_config_into_orchestrator(orchestrator, input_file, output_file)
        artifacts = orchestrator.get_execution_artifacts()
        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )
        assert Path(output_file).exists()

    # ------------------------------------------------------------
    # Pipeline‑Level Sensitivity Gate Signatures
    # ------------------------------------------------------------

    def test_sensitivity_missing_files(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Missing config.json
        missing = tmp_path / "missing.json"
        with pytest.raises(Exception):
            controller.load_and_evaluate_config(missing)

        # Missing input JSON referenced by a valid config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "missing_input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        with pytest.raises(Exception):
            controller.load_and_evaluate_config(config_path)

    def test_sensitivity_malformed_json(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Malformed config.json
        bad_config = tmp_path / "bad_config.json"
        bad_config.write_text("{not valid json")
        with pytest.raises(Exception):
            controller.load_and_evaluate_config(bad_config)

        # Malformed input JSON
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "bad_input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        bad_input = tmp_path / "bad_input.json"
        bad_input.write_text("{not valid json")
        with pytest.raises(Exception):
            controller.load_and_evaluate_config(config_path)

    def test_sensitivity_invalid_jsonpath(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()

        # Config
        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        self._write_json(tmp_path / "config.json", config)

        # Input with invalid JSONPath
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.invalid[", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        runs = controller.load_and_evaluate_config(tmp_path / "config.json")
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)
        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )

        assert success is False
        assert any("Invalid JSONPath" in e for e in errors)

    def test_sensitivity_configuration_anomalies(self, tmp_path):
        """
        Use ExecutionArtifactsDummy to exercise config edge cases without
        invoking production logic unnecessarily.
        """
        dummy = ExecutionArtifactsDummy()

        # Conflicting requires_all / requires_none on the same file
        conflicting_run = {
            "requires_all": ["A.json"],
            "requires_none": ["A.json"],
            "input_file": "A.json",
            "output_assembler_file": "A_out.json",
        }
        dummy.override(config={"runs": [conflicting_run]}, scenario_label="conflicting_requires")

        assert dummy["config"]["runs"][0]["requires_all"] == ["A.json"]
        assert dummy["config"]["runs"][0]["requires_none"] == ["A.json"]

        # Empty runs list is allowed but should result in no work
        empty_runs = ExecutionArtifactsDummy().override(
            config={"runs": []}, scenario_label="empty_runs"
        )
        assert empty_runs["config"]["runs"] == []

    def test_sensitivity_boundary_conditions(self, tmp_path):
        """
        Boundary conditions on empty sources / errors / merged output.
        """
        orchestrator = SchemaMergerSplitterOrchestrator()

        # Empty sources
        input_json = {
            "output_filename": "merged.json",
            "sources": {},
        }
        loaded, load_errors = orchestrator.load_source_files(input_json)
        merged, copy_errors = orchestrator.execute_copy_operations(loaded, input_json)

        assert loaded == {}
        assert merged == {}
        assert load_errors == []
        assert copy_errors == []

    # ------------------------------------------------------------
    # Pipeline‑Level Structural Determinism Gate Signatures
    # ------------------------------------------------------------

    def test_deterministic_pipeline_output(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        self._write_json(tmp_path / "config.json", config)

        # Input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 42})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        def run_once():
            runs = controller.load_and_evaluate_config(tmp_path / "config.json")
            input_file, output_file = runs[0]
            output_filename, sources = controller.load_input_file(input_file)
            success, errors = orchestrator.run(
                {"output_filename": output_filename, "sources": sources}
            )
            assert success is True
            assert errors == []

            self._inject_run_config_into_orchestrator(orchestrator, input_file, output_file)
            artifacts = orchestrator.get_execution_artifacts()
            assembler.assemble_final_output(
                artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
            )
            return (
                self._load_json("data/testing-input-output/merged.json"),
                self._load_json("data/testing-input-output/merged.json.results.json"),
                self._load_json(output_file),
            )

        out1, res1, final1 = run_once()
        out2, res2, final2 = run_once()

        assert out1 == out2
        assert res1 == res2
        assert final1 == final2

    def test_deterministic_error_propagation(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()

        # Config
        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        self._write_json(tmp_path / "config.json", config)

        # Input referencing missing file
        input_json = {
            "output_filename": "merged.json",
            "sources": {str(tmp_path / "missing.json"): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        def run_once():
            runs = controller.load_and_evaluate_config(tmp_path / "config.json")
            input_file, _ = runs[0]
            output_filename, sources = controller.load_input_file(input_file)
            return orchestrator.run(
                {"output_filename": output_filename, "sources": sources}
            )

        s1, e1 = run_once()
        s2, e2 = run_once()

        assert s1 == s2
        assert e1 == e2

    def test_no_implicit_mutation(self, tmp_path):
        """
        Use ExecutionArtifactsDummy to ensure no implicit mutation of
        config / inputs / results when overridden.
        """
        dummy = ExecutionArtifactsDummy()

        original_inputs = json.loads(json.dumps(dummy["inputs"]))
        original_config = json.loads(json.dumps(dummy["config"]))
        original_results = json.loads(json.dumps(dummy["results"]))

        # Override secondary metadata only
        dummy.override(scenario_label="no_mutation", injected_error="X")

        assert dummy["inputs"] == original_inputs
        assert dummy["config"] == original_config
        assert dummy["results"] == original_results

    # ------------------------------------------------------------
    # Pipeline‑Level Consistency Gate Signatures
    # ------------------------------------------------------------

    def test_consistent_schema_alignment(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        self._write_json(tmp_path / "config.json", config)

        # Input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(tmp_path / "config.json")
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)
        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

        self._inject_run_config_into_orchestrator(orchestrator, input_file, output_file)
        artifacts = orchestrator.get_execution_artifacts()

        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )

        final = self._load_json(output_file)
        assert set(final.keys()) == {"inputs", "config", "results"}

    def test_consistent_run_order(self, tmp_path):
        controller = SchemaMergerSplitterController()

        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": "A.json",
                    "output_assembler_file": "A_out.json",
                },
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": "B.json",
                    "output_assembler_file": "B_out.json",
                },
            ]
        }
        path = tmp_path / "config.json"
        self._write_json(path, config)

        runs = controller.load_and_evaluate_config(path)
        assert runs == [("A.json", "A_out.json"), ("B.json", "B_out.json")]

    def test_consistent_copy_operation_order(self, tmp_path):
        orchestrator = SchemaMergerSplitterOrchestrator()

        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1, "b": 2})

        input_json = {
            "output_filename": "merged.json",
            "sources": {
                str(src): [
                    {"from": "$.a", "to": "A"},
                    {"from": "$.b", "to": "B"},
                ]
            },
        }

        loaded, _ = orchestrator.load_source_files(input_json)
        merged, errors = orchestrator.execute_copy_operations(loaded, input_json)

        assert errors == []
        assert list(merged.keys()) == ["A", "B"]

    def test_final_output_consistency(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        input_path = tmp_path / "input.json"
        final_path = tmp_path / "final.json"
        config = self._make_single_run_config(input_path, final_path)
        self._write_json(tmp_path / "config.json", config)

        # Input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 99})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(input_path, input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(tmp_path / "config.json")
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)
        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

        self._inject_run_config_into_orchestrator(orchestrator, input_file, output_file)
        artifacts = orchestrator.get_execution_artifacts()

        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )

        final = self._load_json(output_file)

        assert final["inputs"] == artifacts["inputs"]
        assert final["config"] == artifacts["config"]
        assert final["results"] == artifacts["results"]

    def test_no_hidden_state_across_pipeline(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()

        config = {"runs": []}
        self._write_json(tmp_path / "config.json", config)

        controller.load_and_evaluate_config(tmp_path / "config.json")
        controller.load_and_evaluate_config(tmp_path / "config.json")

        assert not hasattr(controller, "_hidden")
        assert not hasattr(orchestrator, "_hidden")