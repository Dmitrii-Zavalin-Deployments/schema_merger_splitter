"""
Schema‑Merger‑Splitter — Top‑Level Pipeline Runner (CLI-Driven Controller)

This file is the ONLY place where the concrete components are linked:

    1. Controller       (Step 2 - Load input JSON)
    2. Orchestrator     (Steps 3–6 - Merge execution)
    3. Output Assembler (Step 7 - Final artifact construction)

None of these components call each other internally.
The Constitution forbids cross‑component calls inside the components themselves.
"""
import argparse
import logging
from pathlib import Path
import sys

from src.controller import SchemaMergerSplitterController
from src.orchestrator import SchemaMergerSplitterOrchestrator
from src.output_assembler import SchemaMergerSplitterOutputAssembler

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
    parser = argparse.ArgumentParser(
        description="Run the Schema-Merger-Splitter pipeline for a single target configuration file."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the JSON input settings file (e.g., building_navier_stokes_output.json)"
    )
    
    # Print help if no arguments are passed
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    input_path = Path(args.input_file).resolve()

    if not input_path.exists():
        logger.error(f"Target input file not found: {input_path}")
        sys.exit(1)

    logger.info("=== Executing Schema-Merger-Splitter Pipeline ===")
    logger.info(f"Target File: {input_path}")

    # ------------------------------------------------------------
    # Step 2 — Load input JSON via Controller
    # ------------------------------------------------------------
    controller = SchemaMergerSplitterController()
    try:
        output_filename, sources = controller.load_input_file(input_path)
        input_json_instance = {
            "output_filename": output_filename,
            "sources": sources
        }
    except Exception as e:
        logger.error(f"Failed to load input file via Controller: {e}")
        sys.exit(1)

    # ------------------------------------------------------------
    # Steps 3–6 — Core Execution via Orchestrator
    # ------------------------------------------------------------
    orchestrator = SchemaMergerSplitterOrchestrator()
    
    # Executing run without legacy config constraints or injections
    success, errors = orchestrator.run(input_json_instance)

    logger.info(f"Execution success status: {success}")
    for e in errors:
        logger.error(f"Execution Error: {e}")

    if not success:
        sys.exit(1)

    # ------------------------------------------------------------
    # Step 7 — Final Output Compilation via Output Assembler
    # ------------------------------------------------------------
    artifacts = orchestrator.get_execution_artifacts()

    assembler = SchemaMergerSplitterOutputAssembler()
    assembler.assemble_final_output(
        artifacts["inputs"],
        artifacts.get("config"),  # Will pass None cleanly if config artifact is entirely omitted
        artifacts["results"],
        input_path
    )

    logger.info(f"Final assembled output successfully synchronized back to: {input_path}")


if __name__ == "__main__":  # pragma: no cover
    main()