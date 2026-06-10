#!/bin/bash
# src/upload_to_dropbox.sh
# 📤 Dropbox Upload Orchestrator — Professional Cloud Export Gate.

# 1. Environment Guard
if [[ -z "${APP_KEY}" || -z "${APP_SECRET}" || -z "${REFRESH_TOKEN}" ]]; then
    echo "❌ ERROR: Missing required credentials."
    exit 1
fi

# 2. Path Resolution
BASE_WORK_DIR=$(pwd)
TARGET_DIR="${BASE_WORK_DIR}/data/testing-input-output"

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ ERROR: Directory not found: $TARGET_DIR"
    exit 1
fi

export PYTHONPATH="${PYTHONPATH}:${BASE_WORK_DIR}"

echo "🔄 Scanning directory for uploadable artifacts: $TARGET_DIR"
FILES=("$TARGET_DIR"/*)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "❌ ERROR: No files found to upload."
    exit 1
fi

# 3. Upload each file
for FILE in "${FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo "🔄 Triggering Python CloudUploader for: $FILE"

        python3 - <<EOF
from pathlib import Path
from src.io.dropbox_utils import TokenManager
from src.io.upload_to_dropbox import CloudUploader
import os

tm = TokenManager(client_id=os.environ['APP_KEY'], client_secret=os.environ['APP_SECRET'])
uploader = CloudUploader(tm, os.environ['REFRESH_TOKEN'])

uploader.upload(Path("$FILE"), "/simulators")
EOF

        if [ $? -eq 0 ]; then
            echo "✅ Successfully uploaded: /simulators/$(basename "$FILE")"
        else
            echo "❌ ERROR: Upload failed for $FILE"
            exit 1
        fi
    fi
done

echo "✅ PIPELINE COMPLETE: All artifacts uploaded successfully."