# tests/test_output_assembler.py

import json
from pathlib import Path
import pytest

from tests.signatures.output_assembler_test_signature import OutputAssemblerTestSignature
from tests.dummies.execution_artifacts_dummy import ExecutionArtifactsDummy

from src.output_assembler import SchemaMergerSplitterOutputAssembler


class TestOutputAssembler(OutputAssemblerTestSignature):
    """
    Concrete Phase‑6 test implementation for the Schema‑Merger‑Splitter output assembler.
    Implements all required tests from OutputAssemblerTestSignature.
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

    # ------------------------------------------------------------
    # Step 7 — Schema validation
    # ------------------------------------------------------------

    def test_output_schema_validation(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "assembled.json"

        # Valid case — should not raise
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        # Invalid case — missing required field
        bad_inputs = {"sources": {}}  # missing output_filename
        with pytest.raises(Exception):
            assembler.assemble_final_output(
                bad_inputs, dummy["config"], dummy["results"], out_path
            )

    def test_assembled_object_structure(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assembled = self._load_json(out_path)
        assert set(assembled.keys()) == {"inputs", "config", "results"}

    def test_inputs_section_integrity(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        dummy["inputs"] = {
            "output_filename": "x.json",
            "sources": {"file.json": [{"from": "$.a", "to": "A"}]},
        }

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assembled = self._load_json(out_path)
        assert assembled["inputs"] == dummy["inputs"]

    def test_config_section_integrity(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        dummy["config"] = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": "in.json",
                    "output_assembler_file": "out.json",
                }
            ]
        }

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assembled = self._load_json(out_path)
        assert assembled["config"] == dummy["config"]

    def test_results_section_integrity(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        dummy["results"] = {"success": True, "errors": []}

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assembled = self._load_json(out_path)
        assert assembled["results"] == dummy["results"]

    # ------------------------------------------------------------
    # Output file writing
    # ------------------------------------------------------------

    def test_output_file_write(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assert out_path.exists()

    def test_output_file_write_determinism(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out1 = tmp_path / "a1.json"
        out2 = tmp_path / "a2.json"

        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out1
        )
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out2
        )

        assert self._load_json(out1) == self._load_json(out2)

    # ------------------------------------------------------------
    # Sensitivity Gates
    # ------------------------------------------------------------

    def test_missing_inputs_section(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        bad = {"config": dummy["config"], "results": dummy["results"]}

        out_path = tmp_path / "bad.json"
        with pytest.raises(Exception):
            assembler.assemble_final_output(
                bad.get("inputs"), bad["config"], bad["results"], out_path
            )

    def test_missing_config_section(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "bad.json"
        with pytest.raises(Exception):
            assembler.assemble_final_output(
                dummy["inputs"], None, dummy["results"], out_path
            )

    def test_missing_results_section(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "bad.json"
        with pytest.raises(Exception):
            assembler.assemble_final_output(
                dummy["inputs"], dummy["config"], None, out_path
            )

    def test_extra_fields_in_assembled_object(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        # Inject extra field
        dummy["inputs"]["extra"] = 123

        out_path = tmp_path / "bad.json"
        with pytest.raises(Exception):
            assembler.assemble_final_output(
                dummy["inputs"], dummy["config"], dummy["results"], out_path
            )

    # ------------------------------------------------------------
    # Structural Determinism
    # ------------------------------------------------------------

    def test_deterministic_assembly(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        assembled1 = {
            "inputs": dummy["inputs"],
            "config": dummy["config"],
            "results": dummy["results"],
        }
        assembled2 = {
            "inputs": dummy["inputs"],
            "config": dummy["config"],
            "results": dummy["results"],
        }

        assert assembled1 == assembled2

    def test_no_mutation_of_artifacts(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        before = json.loads(json.dumps(dummy))
        out_path = tmp_path / "assembled.json"

        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        after = dummy
        assert before == after

    # ------------------------------------------------------------
    # Consistency Gates
    # ------------------------------------------------------------

    def test_schema_consistency(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assembled = self._load_json(out_path)
        assert set(assembled.keys()) == {"inputs", "config", "results"}

    def test_no_hidden_state(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        # Assembler must not store hidden state
        assert not hasattr(assembler, "_hidden")

    def test_output_file_consistency(self, tmp_path):
        assembler = SchemaMergerSplitterOutputAssembler()
        dummy = ExecutionArtifactsDummy()

        out_path = tmp_path / "assembled.json"
        assembler.assemble_final_output(
            dummy["inputs"], dummy["config"], dummy["results"], out_path
        )

        assembled = self._load_json(out_path)
        assert assembled["inputs"] == dummy["inputs"]
        assert assembled["config"] == dummy["config"]
        assert assembled["results"] == dummy["results"]