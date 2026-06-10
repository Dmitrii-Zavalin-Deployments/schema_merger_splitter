# src/orchestrator.py

import json
from pathlib import Path

from jsonschema import validate
from jsonpath_ng import parse as jsonpath_parse

from .interfaces.orchestrator_interface import SchemaMergerSplitterOrchestratorInterface


class SchemaMergerSplitterOrchestrator(SchemaMergerSplitterOrchestratorInterface):
    """
    Concrete implementation of the Schema‑Merger‑Splitter orchestrator.

    Implements:
        Step 2  — Validate input JSON
        Step 3  — Load source files
        Step 4  — Execute copy operations
        Step 5  — Write merged output
        Step 6  — Write results JSON
        Step 7  — Expose execution artifacts
        run()   — Execute Steps 2–6 in strict order

    No defaults are introduced. The controller MUST inject a validated config.
    """

    # ------------------------------------------------------------
    # Step 2 — Validate input JSON
    # ------------------------------------------------------------
    def validate_input_json(self, input_json_instance):
        """
        Validate the input JSON against the frozen Input Schema.
        Detect:
            - missing required fields
            - extra fields
            - incorrect types
        """
        base_dir = Path(__file__).resolve().parents[1]
        schema_path = base_dir / "schema" / "schema_merger_splitter_input_schema.json"

        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)

        validate(instance=input_json_instance, schema=schema)

    # ------------------------------------------------------------
    # Step 3 — Load all source JSON files
    # ------------------------------------------------------------
    def load_source_files(self, input_json_instance):
        """
        Load all source files referenced in input_json_instance["sources"].

        Returns:
            loaded_sources: dict(filename → JSON object)
            errors: list of error messages
        """
        base_dir = Path(__file__).resolve().parents[1]

        loaded_sources = {}
        errors = []

        for filename in input_json_instance["sources"].keys():
            path = Path(filename)
            if not path.is_absolute():
                path = base_dir / filename

            if not path.exists():
                errors.append(f"Missing source file: {filename}")
                continue

            try:
                with path.open("r", encoding="utf-8") as f:
                    loaded_sources[filename] = json.load(f)
            except Exception as e:
                errors.append(f"Unreadable source file '{filename}': {e}")

        return loaded_sources, errors

    # ------------------------------------------------------------
    # Step 4 — Execute copy operations
    # ------------------------------------------------------------
    def execute_copy_operations(self, loaded_sources, input_json_instance):
        """
        Execute one copy operation per mapping:
            - Evaluate JSONPath
            - Detect missing fields
            - Detect duplicate 'to' keys
            - Insert extracted values into merged output

        Returns:
            merged_output: dict
            errors: list of error messages
        """
        merged_output = {}
        errors = []

        for filename, mappings in input_json_instance["sources"].items():
            source_json = loaded_sources.get(filename)

            if source_json is None:
                continue  # Missing file already recorded

            for mapping in mappings:
                jsonpath_expr = mapping["from"]
                to_key = mapping["to"]

                # Duplicate 'to' key detection
                if to_key in merged_output:
                    errors.append(f"Duplicate target key '{to_key}'")
                    continue

                try:
                    expr = jsonpath_parse(jsonpath_expr)
                    matches = [m.value for m in expr.find(source_json)]
                except Exception as e:
                    errors.append(f"Invalid JSONPath '{jsonpath_expr}': {e}")
                    continue

                if not matches:
                    errors.append(
                        f"Missing field for JSONPath '{jsonpath_expr}' in '{filename}'"
                    )
                    continue

                # JSONPath may return multiple values; use the first
                merged_output[to_key] = matches[0]

        return merged_output, errors

    # ------------------------------------------------------------
    # Step 5 — Write merged output file
    # ------------------------------------------------------------
    def write_merged_output(self, merged_output, input_json_instance):
        """
        Write merged_output to:
            data/testing-input-output/<output_filename>

        Only executed if no fatal errors occurred.
        """
        base_dir = Path(__file__).resolve().parents[1]
        output_dir = base_dir / "data" / "testing-input-output"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = input_json_instance["output_filename"]
        output_path = output_dir / output_filename

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(merged_output, f, indent=2)

    # ------------------------------------------------------------
    # Step 6 — Write results JSON
    # ------------------------------------------------------------
    def write_results_json(self, success, errors, input_json_instance):
        """
        Always write the results JSON containing:
            {
                "success": <bool>,
                "errors": <list of strings>
            }
        """
        base_dir = Path(__file__).resolve().parents[1]
        output_dir = base_dir / "data" / "testing-input-output"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_filename = input_json_instance["output_filename"] + ".results.json"
        output_path = output_dir / output_filename

        results_obj = {
            "success": success,
            "errors": errors,
        }

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(results_obj, f, indent=2)

        # Store for Step 7
        self._results = results_obj
        self._inputs = input_json_instance

        # IMPORTANT:
        # The controller MUST inject a validated config before Step 7 is used.
        # No defaults are allowed.
        if not hasattr(self, "_config"):
            raise RuntimeError(
                "Orchestrator missing validated config. "
                "Controller must set orchestrator._config before artifacts are requested."
            )

    # ------------------------------------------------------------
    # Step 7 — Expose execution artifacts
    # ------------------------------------------------------------
    def get_execution_artifacts(self):
        """
        Return:
            {
                "inputs":  <validated input JSON>,
                "config":  <validated config entry>,
                "results": <results JSON>
            }
        """
        return {
            "inputs": self._inputs,
            "config": self._config,  # MUST be injected by controller
            "results": self._results,
        }

    # ------------------------------------------------------------
    # Full Minimal Step Path executor
    # ------------------------------------------------------------
    def run(self, input_json_instance):
        """
        Execute Steps 2–6 in strict order.
        """
        # Step 2 — Validate input JSON
        self.validate_input_json(input_json_instance)

        # Step 3 — Load source files
        loaded_sources, load_errors = self.load_source_files(input_json_instance)

        # Step 4 — Execute copy operations
        merged_output, copy_errors = self.execute_copy_operations(
            loaded_sources, input_json_instance
        )

        all_errors = load_errors + copy_errors
        success = len(all_errors) == 0

        # Step 5 — Write merged output (only if success)
        if success:
            self.write_merged_output(merged_output, input_json_instance)

        # Step 6 — Always write results JSON
        self.write_results_json(success, all_errors, input_json_instance)

        return success, all_errors