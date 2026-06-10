#!/usr/bin/env bash
# src/debug/forensic_audit.sh
#
# Post‑test forensic audit for Schema‑Merger‑Splitter pipeline.
# Designed to run in GitHub Actions after pytest, to surface root causes
# and provide automated‑repair hints (sed lines are commented out).

set -euo pipefail

echo "=== FORENSIC AUDIT: START ==="

echo
echo "=== 1. Show failing test summary (if available) ==="
if [ -f ".pytest_cache/v/cache/lastfailed" ]; then
  cat .pytest_cache/v/cache/lastfailed || true
fi

echo
echo "=== 2. Grep for orchestrator config guard and artifacts usage ==="
grep -n "get_execution_artifacts" -R src tests || true
grep -n "_config" -R src tests || true
grep -n "assemble_final_output" -R src tests || true

echo
echo "=== 3. Show smoking‑gun source around orchestrator artifacts ==="
echo "--- FILE: src/orchestrator.py ---"
if [ -f "src/orchestrator.py" ]; then
  nl -ba src/orchestrator.py | sed -n '160,230p' || true
fi

echo
echo "--- FILE: src/output_assembler.py ---"
if [ -f "src/output_assembler.py" ]; then
  nl -ba src/output_assembler.py | sed -n '1,260p' || true
fi

echo
echo "--- FILE: tests/test_pipeline_unified.py ---"
if [ -f "tests/test_pipeline_unified.py" ]; then
  nl -ba tests/test_pipeline_unified.py | sed -n '1,260p' || true
  nl -ba tests/test_pipeline_unified.py | sed -n '260,520p' || true
fi

echo
echo "=== 4. Show schema definitions for config/output/results ==="
if [ -d "schema" ]; then
  echo "--- schema_merger_splitter_config.schema.json ---"
  nl -ba schema/schema_merger_splitter_config.schema.json | sed -n '1,260p' || true

  echo
  echo "--- schema_merger_splitter_output_schema.json ---"
  nl -ba schema/schema_merger_splitter_output_schema.json | sed -n '1,260p' || true

  echo
  echo "--- schema_merger_splitter_results_schema.json ---"
  nl -ba schema/schema_merger_splitter_results_schema.json | sed -n '1,260p' || true
fi

echo
echo "=== 5. Inspect latest pipeline outputs (if any) ==="
if [ -d "data/testing-input-output" ]; then
  echo "--- ls -l data/testing-input-output ---"
  ls -l data/testing-input-output || true

  echo
  echo "--- cat merged.json (if exists) ---"
  if [ -f "data/testing-input-output/merged.json" ]; then
    cat data/testing-input-output/merged.json || true
  fi

  echo
  echo "--- cat merged.json.results.json (if exists) ---"
  if [ -f "data/testing-input-output/merged.json.results.json" ]; then
    cat data/testing-input-output/merged.json.results.json || true
  fi
fi

echo
echo "=== 6. Inspect ExecutionArtifactsDummy for config shape ==="
if [ -f "tests/dummies/execution_artifacts_dummy.py" ]; then
  nl -ba tests/dummies/execution_artifacts_dummy.py | sed -n '1,260p' || true
fi

echo
echo "=== 7. Focused audit: helper injecting orchestrator._config in pipeline tests ==="
if [ -f "tests/test_pipeline_unified.py" ]; then
  grep -n "_inject_run_config_into_orchestrator" -n tests/test_pipeline_unified.py || true
  nl -ba tests/test_pipeline_unified.py | sed -n '40,120p' || true
fi

echo
echo "=== 8. DIAGNOSTIC NOTE ==="
echo "The failing ValidationError shows instance['config'] is a single run entry:"
echo "  {\"requires_all\": [], \"requires_none\": [], \"input_file\": ..., \"output_assembler_file\": ...}"
echo "but the config schema expects:"
echo "  {\"runs\": [ {\"requires_all\": [], \"requires_none\": [], \"input_file\": ..., \"output_assembler_file\": ...} ]}"
echo
echo "This strongly suggests that the helper which injects orchestrator._config for"
echo "execution artifacts should wrap the run entry inside a top‑level 'runs' array,"
echo "so that artifacts['config'] matches schema_merger_splitter_config.schema.json."

echo
echo "=== 9. SUGGESTED AUTOMATED REPAIRS (COMMENTED sed COMMANDS) ==="
echo "# The goal: make orchestrator._config a schema‑valid config object:"
echo "#   {\"runs\": [<single_run_entry>]}"
echo "# instead of a bare single_run_entry dict."

echo
echo "# 9.1 Patch tests/test_pipeline_unified.py helper _inject_run_config_into_orchestrator"
echo "# Current shape (for reference):"
echo "#   def _inject_run_config_into_orchestrator(self, orchestrator, input_file, output_file):"
echo "#       orchestrator._config = {"
echo "#           \"requires_all\": [],"
echo "#           \"requires_none\": [],"
echo "#           \"input_file\": str(input_file),"
echo "#           \"output_assembler_file\": str(output_file),"
echo "#       }"
echo "#"
echo "# Desired shape:"
echo "#   def _inject_run_config_into_orchestrator(self, orchestrator, input_file, output_file):"
echo "#       orchestrator._config = {"
echo "#           \"runs\": ["
echo "#               {"
echo "#                   \"requires_all\": [],"
echo "#                   \"requires_none\": [],"
echo "#                   \"input_file\": str(input_file),"
echo "#                   \"output_assembler_file\": str(output_file),"
echo "#               }"
echo "#           ]"
echo "#       }"
echo "#"
echo "# Example sed patch (may need tweaking for exact spacing/indentation):"
echo "# sed -i \"s/orchestrator._config = {\\$/orchestrator._config = {\\\\n            \\\"runs\\\": [\\\\n                {\\\\n                    \\\"requires_all\\\": [],\\\\n                    \\\"requires_none\\\": [],\\\\n                    \\\"input_file\\\": str(input_file),\\\\n                    \\\"output_assembler_file\\\": str(output_file),\\\\n                }\\\\n            ]\\\\n        }/\" tests/test_pipeline_unified.py"

echo
echo "# 9.2 (Optional) Assert that artifacts['config'] is always schema‑shaped"
echo "# You can add a quick debug assertion in tests/test_pipeline_unified.py"
echo "# near final_output_consistency to confirm:"
echo "#   assert set(artifacts['config'].keys()) == {'runs'}"
echo "#   assert isinstance(artifacts['config']['runs'], list)"

echo
echo "=== FORENSIC AUDIT: END ==="