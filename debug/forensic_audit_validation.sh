#!/bin/bash

echo "=== [Forensic Audit: Main Script Path Mismatch Analysis] ==="

# 1. Capture environment state and process details
echo "--- [Environment & Directory State] ---"
echo "Execution User: $(whoami)"
echo "Current Working Directory: $(pwd)"
echo "Locating all JSON configuration files inside workspace:"
find . -name "*.json" -not -path "*/.*"

echo "------------------------------------------------"

# 2. Audit the smoking-gun script initialization blocks via cat -n
echo "--- [Source Audit: Main Script Block Execution Context] ---"
if [ -f "src/main.py" ]; then
    # Audit how base_dir and input payloads are loaded when running directly
    cat -n src/main.py | tail -n 40
else
    echo "CRITICAL: src/main.py not found at current root."
fi

echo "------------------------------------------------"

# 3. Use grep to trace where input configurations specify validation filenames
echo "--- [Source Audit: Target Payload References] ---"
grep -rn "validation_input_" src/ tests/ 2>/dev/null || echo "No hardcoded string references found in codebases."

echo "=== [Automated Repair Injections] ==="
# Strategy A: Copy files to workspace root if src/main.py resolves files relative to '.'
# # cp data/testing-input-output/validation_input_*.json .

# Strategy B: If main.py reads from a task description (e.g. data/validation_task.json) that points to bare filenames, re-route it
# # sed -i 's|"validation_input_1.json"|"data/testing-input-output/validation_input_1.json"|g' data/validation_task.json 2>/dev/null

# Strategy C: Force main's execution base_dir variable to explicitly target the testing track folder
# # sed -i 's|base_dir = .*|base_dir = Path("data/testing-input-output")|g' src/main.py

echo "=== [Audit Complete] ==="