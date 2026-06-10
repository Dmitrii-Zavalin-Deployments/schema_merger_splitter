# tests/test_pipeline_unified.py

import json
from copy import deepcopy
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

    def _cleanup_testing_output(self):
        base_dir = Path(__file__).resolve().parents[1]
        out_dir = base_dir / "data" / "testing-input-output"
        for name in ["merged.json", "merged.json.results.json"]:
            p = out_dir / name
            if p.exists():
                p.unlink()

    def _inject_config_into_orchestrator(self, orchestrator, config_dict):
        # Inject the single run entry as the orchestrator config
        runs = config_dict.get("runs", [])
        orchestrator._config = runs[0] if runs else {"runs": []}

    # ------------------------------------------------------------
    # End‑to‑End Pipeline Behaviour
    # ------------------------------------------------------------

    def test_full_pipeline_execution(self, tmp_path):
        """
        Steps 1–7 must execute in strict order.
        """
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Step 1: config.json
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Step 2: input JSON
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        # Execute pipeline
        runs = controller.load_and_evaluate_config(config_path)
        assert len(runs) == 1

        input_file, output_file = runs[0]
        output_filename, sources = controller.load_input_file(input_file)

        # Inject config into orchestrator for artifacts
        self._inject_config_into_orchestrator(orchestrator, config)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

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
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Valid config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Valid input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 10})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(config_path)
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)

        self._inject_config_into_orchestrator(orchestrator, config)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

        artifacts = orchestrator.get_execution_artifacts()
        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )

        # All outputs must exist
        assert Path("data/testing-input-output/merged.json").exists()
        assert Path("data/testing-input-output/merged.json.results.json").exists()
        assert Path(output_file).exists()

    def test_pipeline_failure_case(self, tmp_path):
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Input referencing missing source file
        input_json = {
            "output_filename": "merged.json",
            "sources": {str(tmp_path / "missing.json"): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(config_path)
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)

        self._inject_config_into_orchestrator(orchestrator, config)

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
        artifacts = orchestrator.get_execution_artifacts()
        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )
        assert Path(output_file).exists()

    # ------------------------------------------------------------
    # Sensitivity Gates
    # ------------------------------------------------------------

    def test_sensitivity_missing_files(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Missing config.json
        missing = tmp_path / "missing.json"
        with pytest.raises(Exception):
            controller.load_and_evaluate_config(missing)

        # Missing input JSON referenced in config
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

        runs = controller.load_and_evaluate_config(config_path)
        # Controller still returns runs; orchestrator will surface missing file later
        assert runs == [(str(tmp_path / "missing_input.json"), str(tmp_path / "final.json"))]

    def test_sensitivity_malformed_json(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Malformed config.json
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")

        with pytest.raises(Exception):
            controller.load_and_evaluate_config(bad)

    def test_sensitivity_invalid_jsonpath(self, tmp_path):
        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()

        # Config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        self._write_json(tmp_path / "config.json", config)

        # Input with invalid JSONPath
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.invalid[", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        runs = controller.load_and_evaluate_config(tmp_path / "config.json")
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)

        self._inject_config_into_orchestrator(orchestrator, config)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )

        assert success is False
        assert any("Invalid JSONPath" in e for e in errors)

    def test_sensitivity_configuration_anomalies(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Empty runs list
        config_empty = {"runs": []}
        path_empty = tmp_path / "config_empty.json"
        self._write_json(path_empty, config_empty)
        runs = controller.load_and_evaluate_config(path_empty)
        assert runs == []

        # Invalid run entry (missing required fields)
        config_invalid = {"runs": [{"requires_all": [], "requires_none": []}]}
        path_invalid = tmp_path / "config_invalid.json"
        self._write_json(path_invalid, config_invalid)
        with pytest.raises(Exception):
            controller.load_and_evaluate_config(path_invalid)

    def test_sensitivity_boundary_conditions(self, tmp_path):
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Config with single run
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Input with empty sources
        input_json = {
            "output_filename": "merged.json",
            "sources": {},
        }
        self._write_json(tmp_path / "input.json", input_json)

        runs = controller.load_and_evaluate_config(config_path)
        input_file, output_file = runs[0]
        output_filename, sources = controller.load_input_file(input_file)

        self._inject_config_into_orchestrator(orchestrator, config)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )

        # Empty sources → empty merged output, no errors
        assert success is True
        assert errors == []

        artifacts = orchestrator.get_execution_artifacts()
        assembler.assemble_final_output(
            artifacts["inputs"], artifacts["config"], artifacts["results"], output_file
        )

        final = self._load_json(output_file)
        assert final["inputs"]["sources"] == {}
        assert final["results"]["errors"] == []
        assert final["results"]["success"] is True

    # ------------------------------------------------------------
    # Structural Determinism
    # ------------------------------------------------------------

    def test_deterministic_pipeline_output(self, tmp_path):
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        self._write_json(tmp_path / "config.json", config)

        # Input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 42})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        def run_once():
            self._cleanup_testing_output()
            runs = controller.load_and_evaluate_config(tmp_path / "config.json")
            input_file, output_file = runs[0]
            output_filename, sources = controller.load_input_file(input_file)

            self._inject_config_into_orchestrator(orchestrator, config)

            success, errors = orchestrator.run(
                {"output_filename": output_filename, "sources": sources}
            )
            assert success is True
            assert errors == []

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
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        self._write_json(tmp_path / "config.json", config)

        # Input referencing missing file
        input_json = {
            "output_filename": "merged.json",
            "sources": {str(tmp_path / "missing.json"): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        def run_once():
            runs = controller.load_and_evaluate_config(tmp_path / "config.json")
            input_file, _ = runs[0]
            output_filename, sources = controller.load_input_file(input_file)

            self._inject_config_into_orchestrator(orchestrator, config)

            return orchestrator.run(
                {"output_filename": output_filename, "sources": sources}
            )

        s1, e1 = run_once()
        s2, e2 = run_once()

        assert s1 == s2
        assert e1 == e2

    def test_no_implicit_mutation(self, tmp_path):
        """
        The pipeline must not mutate config/input/source JSON or execution artifacts.
        """
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        # Deep copies of primary fields
        inputs_before = deepcopy(dummy["inputs"])
        config_before = deepcopy(dummy["config"])
        results_before = deepcopy(dummy["results"])

        output_file = tmp_path / "final.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], output_file
        )

        # Primary fields must remain unchanged
        assert dummy["inputs"] == inputs_before
        assert dummy["config"] == config_before
        assert dummy["results"] == results_before

    # ------------------------------------------------------------
    # Consistency Gates
    # ------------------------------------------------------------

    def test_consistent_schema_alignment(self, tmp_path):
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        self._write_json(tmp_path / "config.json", config)

        # Input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 1})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(tmp_path / "config.json")
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)

        self._inject_config_into_orchestrator(orchestrator, config)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

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
        self._cleanup_testing_output()

        controller = SchemaMergerSplitterController()
        orchestrator = SchemaMergerSplitterOrchestrator()
        assembler = SchemaMergerSplitterOutputAssembler()

        # Config
        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": str(tmp_path / "input.json"),
                    "output_assembler_file": str(tmp_path / "final.json"),
                }
            ]
        }
        self._write_json(tmp_path / "config.json", config)

        # Input
        src = tmp_path / "src.json"
        self._write_json(src, {"a": 99})

        input_json = {
            "output_filename": "merged.json",
            "sources": {str(src): [{"from": "$.a", "to": "A"}]},
        }
        self._write_json(tmp_path / "input.json", input_json)

        # Run pipeline
        runs = controller.load_and_evaluate_config(tmp_path / "config.json")
        input_file, output_file = runs[0]

        output_filename, sources = controller.load_input_file(input_file)

        self._inject_config_into_orchestrator(orchestrator, config)

        success, errors = orchestrator.run(
            {"output_filename": output_filename, "sources": sources}
        )
        assert success is True
        assert errors == []

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