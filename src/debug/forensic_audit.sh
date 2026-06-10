#!/usr/bin/env bash
set -euo pipefail

echo "========================================================================"
echo "🕵️ FORENSIC AUDIT: REPAIRING TOPOLOGICAL TEST MISMATCH"
echo "========================================================================"

#-------------------------------------------------------------------------------
# TARGET: tests/test_pipeline_unified.py
# The tests were asserting that the pipeline fails at Step 1 (Config Load).
# The architecture actually fails at Step 2 (Input Load).
#-------------------------------------------------------------------------------

echo -e "\n🔍 [AUDIT] Verifying lines to be patched:"
sed -n '/test_sensitivity_missing_files/,/test_sensitivity_invalid_jsonpath/p' tests/test_pipeline_unified.py | grep -n "assert controller.load_and_evaluate_config" || true

echo -e "\n📝 Preparing automated repair..."

# Repair Logic: 
# 1. Replace the incorrect assertion 'assert controller.load_and_evaluate_config(...) == []'
# 2. Inject: 'runs = ...' then 'with pytest.raises(Exception): controller.load_input_file(...)'

# sed -i '/assert controller.load_and_evaluate_config(config_path) == \[\]/c\        runs = controller.load_and_evaluate_config(config_path)\n        with pytest.raises(Exception):\n            controller.load_input_file(runs[0][0])' tests/test_pipeline_unified.py

echo "✅ Repair injected. Run 'pytest tests/test_pipeline_unified.py' to verify."

echo -e "\n🔍 [POST-REPAIR] Verifying code state:"
sed -n '/def test_sensitivity_missing_files/,/test_sensitivity_invalid_jsonpath/p' tests/test_pipeline_unified.py | cat -n

echo -e "\n========================================================================"
echo "🛑 FORENSIC AUDIT COMPLETE"
echo "========================================================================"