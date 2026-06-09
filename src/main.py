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

from pathlib import Path
import json

from controller import SchemaMergerSplitterController
from orchestrator import SchemaMergerSplitterOrchestrator
from output_assembler import SchemaMergerSplitterOutputAssembler


def main():
    base_dir = Path(__file__).resolve().parents[1]
    config_path = base_dir / "config" / "config.json"

    # ------------------------------------------------------------
    # Stage 1 — Build run list using the controller
    # ------------------------------------------------------------
    controller = SchemaMergerSplitterController()
    runs = controller.load_and_evaluate_config(config_path)

    if not runs:
        print("No runs activated by config conditions.")
        return

    # ------------------------------------------------------------
    # Stage 2 — Execute each run in order
    # ------------------------------------------------------------
    for input_file, output_assembler_file in runs:
        print(f"\n=== Executing run ===")
        print(f"Input file: {input_file}")
        print(f"Output assembler file: {output_assembler_file}")

        # Step 2 — Load input JSON
        output_filename, sources = controller.load_input_file(input_file)
        input_json_instance = {
            "output_filename": output_filename,
            "sources": sources
        }

        # Steps 3–6 — Orchestrator
        orchestrator = SchemaMergerSplitterOrchestrator()
        success, errors = orchestrator.run(input_json_instance)

        print(f"Run success: {success}")
        if errors:
            print("Errors:")
            for e in errors:
                print(f"  - {e}")

        # Step 7 — Output Assembler
        artifacts = orchestrator.get_execution_artifacts()

        assembler = SchemaMergerSplitterOutputAssembler()
        assembler.assemble_final_output(
            artifacts["inputs"],
            artifacts["config"],   # currently None until config is passed through
            artifacts["results"],
            output_assembler_file
        )

        print(f"Final assembled output written to: {output_assembler_file}")


if __name__ == "__main__":
    main()