# src/controller.py

import json
from pathlib import Path

from jsonschema import validate

from src.interfaces.controller_interface import SchemaMergerSplitterControllerInterface


class SchemaMergerSplitterController(SchemaMergerSplitterControllerInterface):
    """
    Concrete implementation of the Schema‑Merger‑Splitter controller.

    Implements:
        Step 2 — Load the merger‑splitter input file

    No defaults are introduced. All required fields must be present.
    """

    # ------------------------------------------------------------
    # Step 2 — Load the merger‑splitter input file
    # ------------------------------------------------------------
    def load_input_file(self, input_file_path):
        """
        Load the merger‑splitter input JSON referenced by input_file_path.

        Returns:
            output_filename: str
            sources: dict mapping source filenames → list of {from, to} rules
        """
        base_dir = Path(__file__).resolve().parents[1]

        # Normalize input file path (relative to project root if not absolute)
        input_path = Path(input_file_path)

        # Default directory for all input files
        default_input_dir = base_dir / "data" / "testing-input-output"

        if not input_path.is_absolute():
            input_path = default_input_dir / input_file_path

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with input_path.open("r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Validate against frozen Input Schema
        input_schema_path = base_dir / "schema" / "schema_merger_splitter_input_schema.json"
        with input_schema_path.open("r", encoding="utf-8") as f:
            input_schema = json.load(f)

        validate(instance=input_data, schema=input_schema)

        # REQUIRED fields — no defaults allowed
        if "output_filename" not in input_data:
            raise ValueError("Input JSON missing required field 'output_filename'.")
        if "sources" not in input_data:
            raise ValueError("Input JSON missing required field 'sources'.")

        output_filename = input_data["output_filename"]
        sources = input_data["sources"]

        if not isinstance(output_filename, str):
            raise ValueError("Field 'output_filename' must be a string.")
        if not isinstance(sources, dict):
            raise ValueError("Field 'sources' must be a dict mapping filenames to copy rules.")

        return output_filename, sources