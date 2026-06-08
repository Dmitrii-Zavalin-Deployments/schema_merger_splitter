# src/input_loader.py

import json
import os
import jsonschema

from .interfaces.input_loader_interface import InputLoaderInterface


class InputLoader(InputLoaderInterface):
    """
    Concrete implementation of InputLoaderInterface.

    Responsibilities:
    - Load the input JSON file.
    - Validate it against the frozen Input Schema.
    - Enforce required fields: 'output_filename' and 'sources'.
    - Enforce structural correctness of mapping rules.
    - Raise errors immediately on any structural violation.
    - Return the parsed JSON object exactly as provided.

    No defaults, no silent corrections, no speculative behaviour.
    """

    def __init__(self):
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "schema",
            "schema_merger_splitter_input_schema.json"
        )

        with open(schema_path, "r", encoding="utf-8") as f:
            self._schema = json.load(f)

    def load_and_validate_input(self, input_file_path):
        """
        Load and validate the input JSON.

        Raises:
            FileNotFoundError
            json.JSONDecodeError
            jsonschema.ValidationError
            ValueError
            TypeError

        Returns:
            dict — the validated input JSON
        """

        # --- File existence ---
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input JSON file not found: {input_file_path}")

        # --- Load JSON ---
        with open(input_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # --- Schema validation ---
        jsonschema.validate(instance=data, schema=self._schema)

        # --- Required fields (schema enforces, but we enforce deterministically too) ---
        if "output_filename" not in data:
            raise ValueError("Missing required field: 'output_filename'")

        if "sources" not in data:
            raise ValueError("Missing required field: 'sources'")

        # --- Type checks ---
        if not isinstance(data["output_filename"], str):
            raise TypeError("'output_filename' must be a string")

        if not isinstance(data["sources"], dict):
            raise TypeError("'sources' must be an object mapping filenames to rule arrays")

        # --- Validate mapping rules ---
        for filename, rules in data["sources"].items():

            if not isinstance(filename, str):
                raise TypeError("All keys in 'sources' must be strings (filenames)")

            if not isinstance(rules, list):
                raise TypeError(f"Rules for source '{filename}' must be a list")

            for rule in rules:
                if not isinstance(rule, dict):
                    raise TypeError(f"Each rule in '{filename}' must be an object")

                if "from" not in rule:
                    raise ValueError(f"Rule in '{filename}' missing required field: 'from'")

                if "to" not in rule:
                    raise ValueError(f"Rule in '{filename}' missing required field: 'to'")

                if not isinstance(rule["from"], str):
                    raise TypeError(f"'from' in '{filename}' must be a string")

                if not isinstance(rule["to"], str):
                    raise TypeError(f"'to' in '{filename}' must be a string")

        # All checks passed
        return data