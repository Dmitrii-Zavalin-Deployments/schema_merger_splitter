import json
import os
from jsonschema import validate, ValidationError


class OutputAssembly:
    """
    Deterministic assembler for the Schema‑Merger‑Splitter final output object.
    Performs no business logic, no transformations, and no derived computations.
    """

    def __init__(self, output_schema):
        """
        Parameters
        ----------
        output_schema : dict
            The frozen Output Schema loaded from schema/schema_merger_splitter_output_schema.json
        """
        self.output_schema = output_schema

    def assemble(self, input_json_instance, config_instance, results_instance):
        """
        Assemble the final output JSON object according to the frozen Output Schema.

        This function performs only:
        - deterministic structural assembly
        - schema validation

        No transformations, no defaults, and no derived computations are permitted.
        """

        # 1. Deterministic structural assembly
        output_object = {
            "inputs": input_json_instance,
            "config": config_instance,
            "results": results_instance,
        }

        # 2. Validate against the frozen Output Schema
        try:
            validate(instance=output_object, schema=self.output_schema)
        except ValidationError as e:
            raise ValueError(
                f"Output assembly failed schema validation: {str(e)}"
            )

        return output_object

    def write(self, output_object, output_filename):
        """
        Write the final output JSON to the designated output directory.
        """

        base_path = "data/testing-input-output"
        output_path = os.path.join(base_path, output_filename)

        with open(output_path, "w") as f:
            json.dump(output_object, f, indent=4)