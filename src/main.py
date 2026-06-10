# src/main.py

"""
Schema‑Merger‑Splitter — Top‑Level Pipeline Runner (Two‑Stage Controller)

This file is the ONLY place where the three concrete components are linked:

    1. Controller  (Steps 1–2)
    2. Orchestrator (Steps 3–6)
    3. Output Assembler (Step 7)

None of these components call each other internally.
The Constitution forbids cross‑component calls inside the components themselves.

main.py performs the two‑stage execution model:

    Stage 1 — Use the controller to evaluate config.json and build the run list.
    Stage 2 — For each run:
                - Load input JSON (controller)
                - Execute merge (orchestrator)
                - Assemble final output (output assembler)

This file is NOT part of the Minimal Step Path and is therefore allowed to
instantiate and connect the components.
"""

import logging
from pathlib import Path
import json

from controller import SchemaMergerSplitterController
from orchestrator import SchemaMergerSplitterOrchestrator
from output_assembler import SchemaMergerSplitterOutputAssembler


# ------------------------------------------------------------
# Configure logger
# ------------------------------------------------------------
logger = logging.getLogger("schema_merger_splitter")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    base_dir = Path(__file__).resolve().parents[1]
    config_path = base_dir / "config" / "config.json"

    # ------------------------------------------------------------
    # Stage 1 — Build run list using the controller
    # ------------------------------------------------------------
    controller = SchemaMergerSplitterController()

    # Load + validate config
    runs = controller.load_and_evaluate_config(config_path)

    # Load the validated config JSON itself (no defaults allowed)
    with config_path.open("r", encoding="utf-8") as f:
        validated_config = json.load(f)

    if not runs:
        logger.info("No runs activated by config conditions.")
        return

    # ------------------------------------------------------------
    # Stage 2 — Execute each run in order
    # ------------------------------------------------------------
    for input_file, output_assembler_file in runs:
        logger.info("=== Executing run ===")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Output assembler file: {output_assembler_file}")

        # Step 2 — Load input JSON
        output_filename, sources = controller.load_input_file(input_file)
        input_json_instance = {
            "output_filename": output_filename,
            "sources": sources
        }

        # Steps 3–6 — Orchestrator
        orchestrator = SchemaMergerSplitterOrchestrator()

        # Inject validated config BEFORE run()
        orchestrator._config = validated_config

        success, errors = orchestrator.run(input_json_instance)

        logger.info(f"Run success: {success}")
        for e in errors:
            logger.error(f"Error: {e}")

        # Step 7 — Output Assembler
        artifacts = orchestrator.get_execution_artifacts()

        assembler = SchemaMergerSplitterOutputAssembler()
        assembler.assemble_final_output(
            artifacts["inputs"],
            artifacts["config"],   # now a validated config object
            artifacts["results"],
            output_assembler_file
        )

        logger.info(f"Final assembled output written to: {output_assembler_file}")


if __name__ == "__main__":
    main()