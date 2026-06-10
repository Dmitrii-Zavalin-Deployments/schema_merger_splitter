# src/output_assembler.py

import json
from pathlib import Path
from jsonschema import validate

from .interfaces.output_assembler_interface import (
    SchemaMergerSplitterOutputAssemblerInterface,
)


class SchemaMergerSplitterOutputAssembler(SchemaMergerSplitterOutputAssemblerInterface):
    """
    Concrete implementation of the Schema‑Merger‑Splitter output assembler.

    Implements:
        Step 7 — Assemble final output object
                 Validate against Output Schema
                 Write final assembled output file

    No defaults are introduced. All required fields must be provided explicitly.
    """

    # ------------------------------------------------------------
    # Step 7 — Assemble final output object
    # ------------------------------------------------------------
    def assemble_final_output(self, inputs, config, results, output_assembler_file):
        """
        Assemble the final output object:

            {
                "inputs":  <validated input JSON instance>,
                "config":  <validated config entry>,
                "results": <results JSON instance>
            }

        Validate this object against the frozen Output Schema and write it
        to the file specified by output_assembler_file.
        """

        # ------------------------------------------------------------
        # 1. Enforce required fields BEFORE schema validation
        # ------------------------------------------------------------
        if inputs is None:
            raise ValueError("Final output assembly error: 'inputs' must not be None.")
        if config is None:
            raise ValueError("Final output assembly error: 'config' must not be None.")
        if results is None:
            raise ValueError("Final output assembly error: 'results' must not be None.")

        if not isinstance(inputs, dict):
            raise ValueError("Final output assembly error: 'inputs' must be a dict.")
        if not isinstance(config, dict):
            raise ValueError("Final output assembly error: 'config' must be a dict.")
        if not isinstance(results, dict):
            raise ValueError("Final output assembly error: 'results' must be a dict.")

        # ------------------------------------------------------------
        # 2. Construct final assembled object
        # ------------------------------------------------------------
        assembled = {
            "inputs": inputs,
            "config": config,
            "results": results,
        }

        # ------------------------------------------------------------
        # 3. Validate against frozen Output Schema
        # ------------------------------------------------------------
        base_dir = Path(__file__).resolve().parents[1]
        schema_path = base_dir / "schema" / "schema_merger_splitter_output_schema.json"

        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)

        validate(instance=assembled, schema=schema)

        # ------------------------------------------------------------
        # 4. Normalize output path
        # ------------------------------------------------------------
        output_path = Path(output_assembler_file)
        if not output_path.is_absolute():
            output_path = base_dir / output_assembler_file

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------------------
        # 5. Write final assembled output file
        # ------------------------------------------------------------
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(assembled, f, indent=2)