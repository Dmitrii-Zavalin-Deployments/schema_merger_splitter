#!/usr/bin/env bash
set -euo pipefail

echo "========================================================================"
echo "🕵️ STARTING FORENSIC AUDIT: TEST PIPELINE UNIFIED FAILURES"
echo "========================================================================"

#-------------------------------------------------------------------------------
# FAILURE 1: test_pipeline_failure_case
# Symptom: AssertionError: assert not True (merged.json exists when it shouldn't)
# Root Cause: Missing cleanup/teardown or an inverted assertion check.
#-------------------------------------------------------------------------------
echo -e "\n🔍 [AUDIT] Failure 1: test_pipeline_failure_case"
TARGET_FILE="data/testing-input-output/merged.json"

if [ -f "$TARGET_FILE" ]; then
    echo "⚠️ Found stale/unexpected artifact at: $TARGET_FILE"
    echo "--- File Metadata ---"
    ls -la "$TARGET_FILE"
    echo "--- File Contents (Truncated) ---"
    head -n 20 "$TARGET_FILE"
else
    echo "✅ Target file $TARGET_FILE does not exist in current workspace state."
fi

echo -e "\n📝 Inspection: test_pipeline_failure_case source"
grep -n -C 10 "def test_pipeline_failure_case" tests/test_pipeline_unified.py || true

# Automated Repair Injection Template:
# Ensure the file is unlinked during setup/teardown or fix the boolean assertion
# sed -i '/def test_pipeline_failure_case/a \        import os; os.unlink("data/testing-input-output/merged.json") if os.path.exists("data/testing-input-output/merged.json") else None' tests/test_pipeline_unified.py


#-------------------------------------------------------------------------------
# FAILURES 2 & 3: test_sensitivity_missing_files & test_sensitivity_malformed_json
# Symptom: DID NOT RAISE <class 'Exception'>
# Root Cause: The pipeline logic is swallowing exceptions internally or returning 
#             graceful fallbacks instead of propagating errors under test conditions.
#-------------------------------------------------------------------------------
echo -e "\n🔍 [AUDIT] Failures 2 & 3: Sensitivity Exception Suppression"
echo "📝 Smoking-gun source audit for missing/malformed file handling:"
cat -n tests/test_pipeline_unified.py | sed -n '/test_sensitivity_missing_files/,/test_deterministic_pipeline_output/p'

echo -e "\n🕵️ Grepping pipeline implementation for exception handling ('try/except'):"
grep -n -C 3 -E "try:|except" src/pipeline/*.py tests/test_pipeline_unified.py || true

# Automated Repair Injection Template:
# Force the test to look for a more specific exception or prevent internal catch-all blocks
# sed -i 's/pytest.raises(Exception)/pytest.raises(ValueError)/g' tests/test_pipeline_unified.py


#-------------------------------------------------------------------------------
# FAILURE 4: test_deterministic_pipeline_output
# Symptom: AttributeError: 'str' object has no attribute 'open'
# Root Cause: A raw string path was passed to a method expecting a pathlib.Path 
#             object (or vice-versa), resulting in a crashed `.open()` call.
#-------------------------------------------------------------------------------
echo -e "\n🔍 [AUDIT] Failure 4: test_deterministic_pipeline_output"
echo "📝 Smoking-gun source audit for deterministic pipeline test block:"
cat -n tests/test_pipeline_unified.py | sed -n '/test_deterministic_pipeline_output/,/^$/p'

echo -e "\n🕵️ Tracking '.open(' down in pipeline source files to catch string/Path type mismatches:"
grep -n -H "\.open(" src/**/*.py src/*.py tests/test_pipeline_unified.py || true

# Automated Repair Injection Template:
# Explicitly cast the incoming string path to a Path object where `.open()` is called.
# sed -i 's/open(/Path(\0)/g' src/pipeline/core.py # Replace with specific target signature


echo -e "\n========================================================================"
echo "🛑 FORENSIC AUDIT COMPLETE"
echo "========================================================================"