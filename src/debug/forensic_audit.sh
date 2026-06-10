#!/usr/bin/env bash
set -euo pipefail

echo "=== FORENSIC AUDIT: START ==="

echo
echo "=== 1. Search for undefined 'json' usage across src/ ==="
grep -RIn --color=always 'json\.load' src || true
grep -RIn --color=always 'json\.dump' src || true
grep -RIn --color=always 'json' src/main.py || true

echo
echo "=== 2. Search for missing 'import json' statements ==="
grep -RIn --color=always '^import json' src || true
grep -RIn --color=always '^from .* import json' src || true

echo
echo "=== 3. Show numbered source for main.py (smoking gun) ==="
if [ -f src/main.py ]; then
    echo "--- FILE: src/main.py ---"
    cat -n src/main.py
fi

echo
echo "=== 4. Show context around all json.load calls (safe extraction) ==="

for f in $(grep -RIl 'json\.load' src); do
    echo "--- FILE: $f ---"

    grep -RIn 'json\.load' "$f" | while IFS=: read -r file ln rest; do
        # Skip non-numeric line numbers
        if ! [[ "$ln" =~ ^[0-9]+$ ]]; then
            continue
        fi

        echo "--- $f : line $ln ---"
        start=$((ln-3))
        end=$((ln+3))
        sed -n "${start},${end}p" "$f"
    done

done

echo
echo "=== 5. Proposed automated repair templates (commented out) ==="
echo "# If main.py is missing 'import json', insert it after the first import block"
echo "# sed -i '1,/^from / s/^from /import json\\n&/' src/main.py"
echo
echo "# Alternatively, insert at top of file:"
echo "# sed -i '1s/^/import json\\n/' src/main.py"

echo
echo "=== 6. Diff preview for the first sed (non-destructive) ==="
echo "# sed '1,/^from / s/^from /import json\\n&/' src/main.py | diff -u src/main.py -"

echo
echo "=== FORENSIC AUDIT: END ==="