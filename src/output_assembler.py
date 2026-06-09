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

    No additional public methods or attributes are introduced.
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
        base_dir = Path(__file__).resolve().parents[1]

        # Construct final assembled object
        assembled = {
            "inputs": inputs,
            "config": config,
            "results": results,
        }

        # Load Output Schema
        schema_path = base_dir / "schema" / "schema_merger_splitter_output_schema.json"
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)

        # Validate assembled object
        validate(instance=assembled, schema=schema)

        # Normalize output path
        output_path = Path(output_assembler_file)
        if not output_path.is_absolute():
            output_path = base_dir / output_assembler_file

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write final assembled output file
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(assembled, f, indent=2)