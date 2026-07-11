#!/bin/bash

echo "--- [Forensic Audit: Module Resolution] ---"
echo "Current Directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

echo "--- [Directory Structure Audit] ---"
# Check if interfaces exists in root or src
find . -maxdepth 3 -name "interfaces" -type d

echo "--- [Package Integrity Audit] ---"
# Check if __init__.py exists
if [ -f "interfaces/__init__.py" ]; then
    echo "✅ interfaces/__init__.py exists."
else
    echo "❌ interfaces/__init__.py is MISSING (likely cause of import error)."
fi

echo "--- [Smoking Gun: Test Source Audit] ---"
# Show content of the failing test file
cat -n tests/test_pipeline_interface.py | grep -C 5 "from interfaces"

echo "--- [Resolution Options: Suggested Repairs] ---"
# If the directory is missing, create it.
# If __init__.py is missing, create it.
# If the import path is wrong, update the test file.

# 1. Fix missing package declaration (Commonly resolves ModuleNotFound)
# sed -i '1i __init__.py' interfaces/__init__.py  # (Or use touch)
# touch interfaces/__init__.py

# 2. Fix import path if code is actually in 'src/interfaces'
# sed -i 's|from interfaces.|from src.interfaces.|g' tests/test_pipeline_interface.py
# sed -i 's|from interfaces.|from src.interfaces.|g' tests/test_step_interface.py

# 3. Add current directory to PYTHONPATH if missing
# export PYTHONPATH=$PYTHONPATH:.

echo "--- [Forensic Audit Complete] ---"