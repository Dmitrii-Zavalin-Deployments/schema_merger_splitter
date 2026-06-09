# src/controller.py

import json
import os
from pathlib import Path

from jsonschema import validate

from .interfaces.controller_interface import SchemaMergerSplitterControllerInterface


class SchemaMergerSplitterController(SchemaMergerSplitterControllerInterface):
    """
    Concrete implementation of the Schema‑Merger‑Splitter controller.

    Implements:
        Step 1 — Load and evaluate config/config.json
        Step 2 — Load the merger‑splitter input file

    This class inherits directly and exclusively from
    SchemaMergerSplitterControllerInterface and introduces no additional
    public methods or attributes.
    """

    # ------------------------------------------------------------
    # Step 1 — Load & evaluate config/config.json
    # ------------------------------------------------------------
    def load_and_evaluate_config(self, config_path):
        """
        Load config/config.json and evaluate each run entry in order.

        For each entry:
            - All requires_all files must exist.
            - All requires_none files must NOT exist.

        Returns:
            A list of (input_file, output_assembler_file) tuples
            for all entries whose conditions pass.
        """
        base_dir = Path(__file__).resolve().parents[1]

        # Normalize config path (relative to project root if not absolute)
        config_path = Path(config_path)
        if not config_path.is_absolute():
            config_path = base_dir / "config" / config_path

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as f:
            config_data = json.load(f)

        # Validate against frozen Config Schema
        config_schema_path = base_dir / "schema" / "schema_merger_splitter_config.schema.json"
        with config_schema_path.open("r", encoding="utf-8") as f:
            config_schema = json.load(f)

        validate(instance=config_data, schema=config_schema)

        runs = config_data.get("runs", [])
        if not isinstance(runs, list):
            raise ValueError("Config 'runs' must be a list.")

        activated_runs = []

        for run in runs:
            requires_all = run.get("requires_all", [])
            requires_none = run.get("requires_none", [])
            input_file = run["input_file"]
            output_assembler_file = run["output_assembler_file"]

            # Evaluate requires_all: all listed files must exist
            all_ok = True
            for rel_path in requires_all:
                candidate = base_dir / rel_path
                if not candidate.exists():
                    all_ok = False
                    break

            # Evaluate requires_none: none of the listed files may exist
            none_ok = True
            for rel_path in requires_none:
                candidate = base_dir / rel_path
                if candidate.exists():
                    none_ok = False
                    break

            if all_ok and none_ok:
                activated_runs.append((input_file, output_assembler_file))

        return activated_runs

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
        if not input_path.is_absolute():
            input_path = base_dir / input_file_path

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with input_path.open("r", encoding="utf-8") as f:
            input_data = json.load(f)

        # Validate against frozen Input Schema
        input_schema_path = base_dir / "schema" / "schema_merger_splitter_input_schema.json"
        with input_schema_path.open("r", encoding="utf-8") as f:
            input_schema = json.load(f)

        validate(instance=input_data, schema=input_schema)

        output_filename = input_data["output_filename"]
        sources = input_data["sources"]

        if not isinstance(output_filename, str):
            raise ValueError("Field 'output_filename' must be a string.")
        if not isinstance(sources, dict):
            raise ValueError("Field 'sources' must be a dict mapping filenames to copy rules.")

        return output_filename, sources