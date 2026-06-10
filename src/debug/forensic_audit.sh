#!/usr/bin/env bash
# src/debug/forensic_audit.sh
#
# Forensic audit for:
#   AttributeError: 'str' object has no attribute 'open'
#
# This indicates that output_assembler_file was passed as a STRING,
# and assembler attempted: Path(output_assembler_file).open(...)
#
# This script surfaces the root cause and proposes automated repairs.

set -euo pipefail

echo "=== FORENSIC AUDIT: START ==="

###############################################################################
# 1. Show failing test summary
###############################################################################
echo
echo "=== 1. Last failed tests (if any) ==="
if [ -f ".pytest_cache/v/cache/lastfailed" ]; then
  cat .pytest_cache/v/cache/lastfailed || true
fi

###############################################################################
# 2. Search for all output_assembler_file usage
###############################################################################
echo
echo "=== 2. Grep for output_assembler_file usage ==="
grep -RIn "output_assembler_file" src tests || true

###############################################################################
# 3. Inspect assembler path normalization
###############################################################################
echo
echo "=== 3. Inspect assembler path normalization ==="
nl -ba src/output_assembler.py | sed -n '60,120p' || true

###############################################################################
# 4. Inspect how tests pass output_assembler_file
###############################################################################
echo
echo "=== 4. How tests pass output_assembler_file ==="
grep -RIn "assemble_final_output" tests/test_pipeline_unified.py || true
nl -ba tests/test_pipeline_unified.py | sed -n '1,200p' || true
nl -ba tests/test_pipeline_unified.py | sed -n '200,400p' || true
nl -ba tests/test_pipeline_unified.py | sed -n '400,650p' || true

###############################################################################
# 5. Inspect controller return values
###############################################################################
echo
echo "=== 5. controller.load_and_evaluate_config return values ==="
nl -ba src/controller.py | sed -n '1,200p' || true

###############################################################################
# 6. Inspect orchestrator.get_execution_artifacts
###############################################################################
echo
echo "=== 6. orchestrator.get_execution_artifacts ==="
nl -ba src/orchestrator.py | sed -n '170,240p' || true

###############################################################################
# 7. DIAGNOSTIC SUMMARY
###############################################################################
echo
echo "=== 7. DIAGNOSTIC SUMMARY ==="
echo "The AttributeError indicates:"
echo "  output_assembler_file is a STRING, not a Path object."
echo
echo "Assembler does:"
echo "  output_path = Path(output_assembler_file)"
echo "  if not output_path.is_absolute():"
echo "      output_path = base_dir / output_assembler_file"
echo
echo "If output_assembler_file is a string, then:"
echo "  base_dir / output_assembler_file"
echo "returns a STRING (because / operator is overloaded only for Path)."
echo
echo "Thus output_path becomes a STRING → .open() fails."

###############################################################################
# 8. SUGGESTED AUTOMATED REPAIRS (COMMENTED sed COMMANDS)
###############################################################################
echo
echo "=== 8. Suggested automated repairs (commented sed commands) ==="

echo "# Option A — Fix controller to return Path objects instead of strings"
echo "# sed -i \"s/activated_runs.append((input_file, output_assembler_file))/activated_runs.append((Path(input_file), Path(output_assembler_file)))/\" src/controller.py"

echo
echo "# Option B — Fix tests to wrap output_file in Path() before assembler call"
echo "# sed -i \"s/assemble_final_output(artifacts\

\[\\\"inputs\\\"\\]

, artifacts\

\[\\\"config\\\"\\]

, artifacts\

\[\\\"results\\\"\\]

, output_file)/assemble_final_output(artifacts[\\\"inputs\\\"], artifacts[\\\"config\\\"], artifacts[\\\"results\\\"], Path(output_file))/\" tests/test_pipeline_unified.py"

echo
echo "# Option C — Fix assembler to coerce strings safely"
echo "# sed -i \"s/output_path = Path(output_assembler_file)/output_path = Path(str(output_assembler_file))/\" src/output_assembler.py"

echo
echo "=== FORENSIC AUDIT: END ==="