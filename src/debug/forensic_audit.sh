#!/usr/bin/env bash
set -euo pipefail

echo "========================================================================"
echo "🕵️ STARTING REVISED FORENSIC AUDIT: 3 REMAINING PIPELINE FAILURES"
echo "========================================================================"

#-------------------------------------------------------------------------------
# FAILURE 1: test_pipeline_failure_case
# Symptom: AssertionError: assert not True (where True = exists())
# Root Cause: A hardcoded 'data/testing-input-output/merged.json' artifact from 
#             a previous success test is leaking into this test environment, or 
#             the pipeline isn't isolating its run paths properly.
#-------------------------------------------------------------------------------
echo -e "\n🔍 [AUDIT] Failure 1: test_pipeline_failure_case"
TARGET_FILE="data/testing-input-output/merged.json"

echo "📝 Checking if leaking artifact exists right now:"
if [ -f "$TARGET_FILE" ]; then
    echo "⚠️ Leaked artifact detected: $TARGET_FILE"
    rm -v "$TARGET_FILE"
else
    echo "✅ No stale artifact found in current workspace context."
fi

echo -e "\n📝 Smoking-gun source audit for test_pipeline_failure_case (Lines 173-224):"
cat -n tests/test_pipeline_unified.py | sed -n '173,224p'

# Automated Repair Injection Template:
# Clean up the global path or force isolation inside the test block before orchestration execution
# sed -i '/def test_pipeline_failure_case(self, tmp_path):/a \        import os; os.remove("data/testing-input-output/merged.json") if os.path.exists("data/testing-input-output/merged.json") else None' tests/test_pipeline_unified.py


#-------------------------------------------------------------------------------
# FAILURES 2 & 3: test_sensitivity_missing_files & test_sensitivity_malformed_json
# Symptom: Failed: DID NOT RAISE <class 'Exception'>
# Root Cause: src/controller.py load_and_evaluate_config handles errors gracefully 
#             (returning an empty array or logging), but the test requires an exception.
#-------------------------------------------------------------------------------
echo -e "\n🔍 [AUDIT] Failures 2 & 3: Exception Suppression in Controller"
echo "📝 Smoking-gun source audit for load_and_evaluate_config in src/controller.py:"
cat -n src/controller.py | grep -n -A 40 "def load_and_evaluate_config" || true

echo -e "\n🕵️ Checking for silent try-except blocks inside src/controller.py:"
grep -n -C 4 -E "try:|except" src/controller.py || true

# Automated Repair Injection Templates:
# Option A: If the controller MUST raise exceptions on failures to pass tests:
# sed -i '/except FileNotFoundError:/a \        raise' src/controller.py
# sed -i '/except json.JSONDecodeError:/a \        raise' src/controller.py

# Option B: If the controller design is intentionally graceful, fix the tests to assert empty/failed runs:
# sed -i '/with pytest.raises(Exception):/,/controller.load_and_evaluate_config(missing)/c\        assert controller.load_and_evaluate_config(missing) == []' tests/test_pipeline_unified.py
# sed -i '/with pytest.raises(Exception):/,/controller.load_and_evaluate_config(bad_config)/c\        assert controller.load_and_evaluate_config(bad_config) == []' tests/test_pipeline_unified.py


echo -e "\n========================================================================"
echo "🛑 FORENSIC AUDIT COMPLETE"
echo "========================================================================"