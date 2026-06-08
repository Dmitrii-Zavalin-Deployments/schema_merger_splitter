# src/orchestrator.py

import json
import os
from jsonpath_ng import parse

from .interfaces.orchestrator_interface import SchemaMergerSplitterOrchestratorInterface
from .config_evaluator import ConfigEvaluator
from .input_loader import InputLoader


class SchemaMergerSplitterOrchestrator(SchemaMergerSplitterOrchestratorInterface):
    """
    Concrete implementation of the Schema‑Merger‑Splitter orchestrator.
    Implements the deterministic Minimal Step Path defined in the frozen Constitution.
    """

    def run(self, config_run_entry):
        """
        Execute the full Minimal Step Path for a single activated run.

        Steps:
        1. Evaluate run activation conditions.
        2. Load and validate the input JSON.
        3. Load source files.
        4. Execute copy operations.
        5. Write merged output.
        6. Write results.json.

        Returns the results object defined by the Results Schema.
        """

        evaluator = ConfigEvaluator()
        loader = InputLoader()

        # Step 1 — Evaluate activation
        is_active = evaluator.evaluate_run_conditions(config_run_entry)
        if not is_active:
            results = {"success": False, "errors": ["Run conditions not satisfied."]}
            self.write_results_json(False, ["Run conditions not satisfied."], {})
            return results

        # Step 2 — Load and validate input JSON
        input_json_instance = loader.load_and_validate_input(config_run_entry["input_file"])

        # Step 3 — Validate structure
        success, errors = self.validate_input_json(input_json_instance)
        if not success:
            self.write_results_json(False, errors, input_json_instance)
            return {"success": False, "errors": errors}

        # Step 4 — Load source files
        loaded_sources, load_errors = self.load_source_files(input_json_instance)
        errors.extend(load_errors)

        # Step 5 — Execute copy operations
        merged_output, copy_errors = self.execute_copy_operations(
            loaded_sources, input_json_instance
        )
        errors.extend(copy_errors)

        # Step 6 — Write merged output if no errors
        if len(errors) == 0:
            self.write_merged_output(merged_output, input_json_instance)

        # Step 7 — Always write results.json
        self.write_results_json(len(errors) == 0, errors, input_json_instance)

        return {"success": len(errors) == 0, "errors": errors}

    def validate_input_json(self, input_json_instance):
        required_fields = {"sources", "output_filename"}
        errors = []

        for field in required_fields:
            if field not in input_json_instance:
                errors.append(f"Missing required field: {field}")

        for field in input_json_instance:
            if field not in required_fields:
                errors.append(f"Unexpected field in input: {field}")

        return (len(errors) == 0, errors)

    def load_source_files(self, input_json_instance):
        base_path = "data/testing-input-output"
        loaded = {}
        errors = []

        for filename, mappings in input_json_instance["sources"].items():
            full_path = os.path.join(base_path, filename)

            try:
                with open(full_path, "r") as f:
                    loaded[filename] = json.load(f)
            except Exception as e:
                errors.append(f"Failed to load {filename}: {str(e)}")

        return loaded, errors

    def execute_copy_operations(self, loaded_sources, input_json_instance):
        merged_output = {}
        errors = []

        for filename, mappings in input_json_instance["sources"].items():
            if filename not in loaded_sources:
                continue

            source_json = loaded_sources[filename]

            for mapping in mappings:
                jsonpath_expr = parse(mapping["from"])
                matches = [match.value for match in jsonpath_expr.find(source_json)]

                if len(matches) == 0:
                    errors.append(
                        f"Missing value for JSONPath '{mapping['from']}' in {filename}"
                    )
                    continue

                if mapping["to"] in merged_output:
                    errors.append(
                        f"Duplicate output key '{mapping['to']}' encountered."
                    )
                    continue

                merged_output[mapping["to"]] = matches[0]

        return merged_output, errors

    def write_merged_output(self, merged_output, input_json_instance):
        base_path = "data/testing-input-output"
        output_path = os.path.join(base_path, input_json_instance["output_filename"])

        with open(output_path, "w") as f:
            json.dump(merged_output, f, indent=4)

    def write_results_json(self, success, errors, input_json_instance):
        base_path = "data/testing-input-output"
        results_path = os.path.join(base_path, "results.json")

        results = {
            "success": success,
            "errors": errors,
        }

        with open(results_path, "w") as f:
            json.dump(results, f, indent=4)