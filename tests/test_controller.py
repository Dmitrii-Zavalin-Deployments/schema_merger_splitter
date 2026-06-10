# tests/test_controller.py

import json
from pathlib import Path

import pytest

from tests.signatures.controller_test_signature import ControllerTestSignature

from src.controller import SchemaMergerSplitterController


class TestController(ControllerTestSignature):
    """
    Concrete Phase‑6 test implementation for the Schema‑Merger‑Splitter controller.
    Inherits all required test responsibilities from ControllerTestSignature.
    """

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _write_json(self, path: Path, obj: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)

    # ------------------------------------------------------------
    # Step 1 — Config validation
    # ------------------------------------------------------------

    def test_config_schema_validation(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Valid config
        config = {"runs": []}
        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        # Should not raise
        controller.load_and_evaluate_config(config_path)

        # Invalid config (missing "runs")
        bad_config = {"not_runs": []}
        bad_path = tmp_path / "bad.json"
        self._write_json(bad_path, bad_config)

        with pytest.raises(Exception):
            controller.load_and_evaluate_config(bad_path)

    def test_requires_all_evaluation(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Create a file that exists
        existing = tmp_path / "exists.json"
        existing.write_text("{}")

        config = {
            "runs": [
                {
                    "requires_all": [str(existing)],
                    "requires_none": [],
                    "input_file": "input.json",
                    "output_assembler_file": "out.json",
                }
            ]
        }

        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        runs = controller.load_and_evaluate_config(config_path)
        assert len(runs) == 1

    def test_requires_none_evaluation(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # Create a file that must NOT exist
        forbidden = tmp_path / "forbidden.json"
        forbidden.write_text("{}")

        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [str(forbidden)],
                    "input_file": "input.json",
                    "output_assembler_file": "out.json",
                }
            ]
        }

        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        runs = controller.load_and_evaluate_config(config_path)
        assert runs == []  # must skip

    def test_run_activation_order(self, tmp_path):
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

        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        runs = controller.load_and_evaluate_config(config_path)
        assert runs == [("A.json", "A_out.json"), ("B.json", "B_out.json")]

    def test_run_list_construction(self, tmp_path):
        controller = SchemaMergerSplitterController()

        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": "input1.json",
                    "output_assembler_file": "out1.json",
                }
            ]
        }

        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        runs = controller.load_and_evaluate_config(config_path)
        assert runs == [("input1.json", "out1.json")]

    def test_run_skipping_behavior(self, tmp_path):
        controller = SchemaMergerSplitterController()

        missing = tmp_path / "missing.json"  # does not exist

        config = {
            "runs": [
                {
                    "requires_all": [str(missing)],
                    "requires_none": [],
                    "input_file": "input.json",
                    "output_assembler_file": "out.json",
                }
            ]
        }

        config_path = tmp_path / "config.json"
        self._write_json(config_path, config)

        runs = controller.load_and_evaluate_config(config_path)
        assert runs == []  # skipped

    # ------------------------------------------------------------
    # Step 2 — Input file loading
    # ------------------------------------------------------------

    def test_input_file_loading(self, tmp_path):
        controller = SchemaMergerSplitterController()

        input_json = {
            "output_filename": "merged.json",
            "sources": {"file1.json": [{"from": "$.a", "to": "A"}]},
        }

        input_path = tmp_path / "input.json"
        self._write_json(input_path, input_json)

        output_filename, sources = controller.load_input_file(input_path)
        assert output_filename == "merged.json"
        assert sources == input_json["sources"]

    def test_input_schema_validation(self, tmp_path):
        controller = SchemaMergerSplitterController()

        bad_input = {"not_output_filename": "x"}  # invalid
        input_path = tmp_path / "bad.json"
        self._write_json(input_path, bad_input)

        with pytest.raises(Exception):
            controller.load_input_file(input_path)

    def test_missing_input_file_handling(self, tmp_path):
        controller = SchemaMergerSplitterController()

        missing = tmp_path / "missing.json"
        with pytest.raises(Exception):
            controller.load_input_file(missing)

    # ------------------------------------------------------------
    # Sensitivity Gate Tests
    # ------------------------------------------------------------

    def test_config_sensitivity_cases(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # malformed JSON
        bad_path = tmp_path / "bad.json"
        bad_path.write_text("{not valid json")

        with pytest.raises(Exception):
            controller.load_and_evaluate_config(bad_path)

        # missing required fields
        missing_runs = {"not_runs": []}
        path2 = tmp_path / "bad2.json"
        self._write_json(path2, missing_runs)

        with pytest.raises(Exception):
            controller.load_and_evaluate_config(path2)

    def test_input_sensitivity_cases(self, tmp_path):
        controller = SchemaMergerSplitterController()

        # malformed JSON
        bad_path = tmp_path / "bad.json"
        bad_path.write_text("{not valid json")

        with pytest.raises(Exception):
            controller.load_input_file(bad_path)

        # missing required fields
        missing = {"sources": {}}
        path2 = tmp_path / "bad2.json"
        self._write_json(path2, missing)

        with pytest.raises(Exception):
            controller.load_input_file(path2)

    # ------------------------------------------------------------
    # Structural Determinism
    # ------------------------------------------------------------

    def test_deterministic_run_evaluation(self, tmp_path):
        controller = SchemaMergerSplitterController()

        config = {"runs": []}
        path = tmp_path / "config.json"
        self._write_json(path, config)

        r1 = controller.load_and_evaluate_config(path)
        r2 = controller.load_and_evaluate_config(path)

        assert r1 == r2

    def test_deterministic_input_loading(self, tmp_path):
        controller = SchemaMergerSplitterController()

        input_json = {
            "output_filename": "x.json",
            "sources": {},
        }

        path = tmp_path / "input.json"
        self._write_json(path, input_json)

        a = controller.load_input_file(path)
        b = controller.load_input_file(path)

        assert a == b

    # ------------------------------------------------------------
    # Consistency Gates
    # ------------------------------------------------------------

    def test_no_hidden_state(self, tmp_path):
        controller = SchemaMergerSplitterController()

        config = {"runs": []}
        path = tmp_path / "config.json"
        self._write_json(path, config)

        controller.load_and_evaluate_config(path)
        controller.load_and_evaluate_config(path)

        # No state stored → no attributes beyond methods
        assert not hasattr(controller, "_state")

    def test_no_reordering_or_mutation(self, tmp_path):
        controller = SchemaMergerSplitterController()

        config = {
            "runs": [
                {
                    "requires_all": [],
                    "requires_none": [],
                    "input_file": "A.json",
                    "output_assembler_file": "A_out.json",
                }
            ]
        }

        path = tmp_path / "config.json"
        self._write_json(path, config)

        runs = controller.load_and_evaluate_config(path)
        assert runs == [("A.json", "A_out.json")]

        # Ensure config not mutated
        with path.open() as f:
            loaded = json.load(f)
        assert loaded == config

    def test_schema_consistency(self, tmp_path):
        controller = SchemaMergerSplitterController()

        input_json = {
            "output_filename": "merged.json",
            "sources": {},
        }

        path = tmp_path / "input.json"
        self._write_json(path, input_json)

        output_filename, sources = controller.load_input_file(path)

        assert isinstance(output_filename, str)
        assert isinstance(sources, dict)