# main.py

import json
from src.orchestrator import SchemaMergerSplitterOrchestrator
from src.output_assembly import OutputAssembly


def main():
    # 1. Load config.json
    with open("config/config.json", "r") as f:
        config = json.load(f)

    # 2. Instantiate orchestrator
    orchestrator = SchemaMergerSplitterOrchestrator()

    # 3. Run Phase 4 (Minimal Step Path)
    run_entry = config["runs"][0]
    orchestrator.run(run_entry)

    # 4. Retrieve artifacts for Phase 5
    input_json, config_json, results_json = orchestrator.get_execution_artifacts()

    # 5. Load Output Schema
    with open("schema/schema_merger_splitter_output_schema.json", "r") as f:
        output_schema = json.load(f)

    # 6. Assemble final output
    assembler = OutputAssembly(output_schema)
    final_output = assembler.assemble(input_json, config_json, results_json)

    # 7. Write final output JSON
    assembler.write(final_output, "final_output.json")


if __name__ == "__main__":
    main()