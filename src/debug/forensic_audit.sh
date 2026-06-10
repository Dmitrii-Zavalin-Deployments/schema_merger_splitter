#!/usr/bin/env bash
set -euo pipefail

echo "=== FORENSIC AUDIT: START ==="

echo
echo "=== 1. Search for places where config may become None ==="
grep -RIn --color=always 'config' src || true
grep -RIn --color=always 'config' tests || true
grep -RIn --color=always 'None' src || true

echo
echo "=== 2. Search for pipeline output JSONs produced during tests ==="
find . -maxdepth 4 -type f -name "*.json" | sort

echo
echo "=== 3. Dump pipeline-unified test output (if exists) ==="
if [ -f data/testing-input-output/final.json ]; then
    echo "--- final.json ---"
    cat -n data/testing-input-output/final.json
fi

if [ -f data/testing-input-output/results.json ]; then
    echo "--- results.json ---"
    cat -n data/testing-input-output/results.json
fi

echo
echo "=== 4. Locate the smoking gun: where config=None is created ==="
grep -RIn --color=always 'config = None' src || true
grep -RIn --color=always '"config": None' -R . || true

echo
echo "=== 5. Show full context around pipeline-unified test ==="
TARGET="tests/test_pipeline_unified.py"
if [ -f "$TARGET" ]; then
    echo "--- FILE: $TARGET ---"
    cat -n "$TARGET"
fi

echo
echo "=== 6. Show orchestrator + pipeline sources (numbered) ==="
for f in src/orchestrator.py src/pipeline_unified.py src/*pipeline*.py; do
    if [ -f "$f" ]; then
        echo "--- FILE: $f ---"
        cat -n "$f"
    fi
done

echo
echo "=== 7. Proposed automated repair templates (commented out) ==="
echo "# If config is missing, replace None with {}"
echo "# sed -i \"s/'config': None/'config': {}/\" src/pipeline_unified.py"
echo
echo "# If pipeline returns config=None, force {}"
echo "# sed -i \"s/config = None/config = {}/\" src/pipeline_unified.py"
echo
echo "# If final output builder inserts config=None, rewrite to {}"
echo "# sed -i \"s/\\\"config\\\": None/\\\"config\\\": {}/\" src/pipeline_unified.py"

echo
echo "=== 8. Diff preview for the first sed (non-destructive) ==="
echo "# sed \"s/'config': None/'config': {}/\" src/pipeline_unified.py | diff -u src/pipeline_unified.py -"

echo
echo "=== FORENSIC AUDIT: END ==="