import json
import os
from jsonpath_ng import parse
from .interfaces.orchestrator_interface import SchemaMergerSplitterOrchestratorInterface


class SchemaMergerSplitterOrchestrator(SchemaMergerSplitterOrchestratorInterface):
    """
    Concrete implementation of the Schema‑Merger‑Splitter orchestrator.
    Implements the deterministic sequence defined in the frozen Constitution.
    """

    def run(self, input_json_instance):
        """
        Execute the full Schema‑Merger‑Splitter minimal step path.
        """
        success, errors = self.validate_input_json(input_json_instance)

        if not success:
            self.write_results_json(False, errors, input_json_instance)
            return

        loaded_sources, load_errors = self.load_source_files(input_json_instance)
        errors.extend(load_errors)

        merged_output, copy_errors = self.execute_copy_operations(
            loaded_sources, input_json_instance
        )
        errors.extend(copy_errors)

        if len(errors) == 0:
            self.write_merged_output(merged_output, input_json_instance)

        self.write_results_json(len(errors) == 0, errors, input_json_instance)

    def validate_input_json(self, input_json_instance):
        """
        Validate the input JSON against the Input Schema.
        Reject missing fields, incorrect types, or extra fields.
        """
        required_fields = {"sources", "output_filename"}
        errors = []

        # Check required fields
        for field in required_fields:
            if field not in input_json_instance:
                errors.append(f"Missing required field: {field}")

        # Check for extra fields
        for field in input_json_instance:
            if field not in required_fields:
                errors.append(f"Unexpected field in input: {field}")

        return (len(errors) == 0, errors)

    def load_source_files(self, input_json_instance):
        """
        Load all source files from data/testing-input-output/.
        Missing or unreadable files must be recorded as errors.
        """
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
        """
        Execute one copy operation per mapping:
        - Evaluate JSONPath
        - Detect missing fields
        - Detect duplicate 'to' keys
        - Insert extracted values into the merged output object
        """
        merged_output = {}
        errors = []

        for filename, mappings in input_json_instance["sources"].items():
            if filename not in loaded_sources:
                continue  # Already recorded as error in load step

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
        """
        Write the merged output file to data/testing-input-output/<output_filename>
        only if no errors occurred.
        """
        base_path = "data/testing-input-output"
        output_path = os.path.join(base_path, input_json_instance["output_filename"])

        with open(output_path, "w") as f:
            json.dump(merged_output, f, indent=4)

    def write_results_json(self, success, errors, input_json_instance):
        """
        Always write the results JSON containing:
        - success: bool
        - errors: list of strings
        """
        base_path = "data/testing-input-output"
        results_path = os.path.join(base_path, "results.json")

        results = {
            "success": success,
            "errors": errors,
        }

        with open(results_path, "w") as f:
            json.dump(results, f, indent=4)