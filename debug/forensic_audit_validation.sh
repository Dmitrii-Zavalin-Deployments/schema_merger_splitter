#!/bin/bash
# -----------------------------------------------------------------------------
# Forensic Audit: Schema Merger-Splitter Integrity
# Purpose: Diagnose JSON schema validation failures and identify illegal keys.
# -----------------------------------------------------------------------------

TARGET_FILE="data/testing-input-output/validation_task.json"
SCHEMA_FILE="schema/schema_merger_splitter_input_schema.json"

echo "=== [1/3] Diagnostic: Search for Forbidden Properties ==="
# Search for the specific key that caused the failure
if grep -q "output_filename" "$TARGET_FILE"; then
    echo "CRITICAL: Illegal property 'output_filename' found in $TARGET_FILE"
    grep -C 3 "output_filename" "$TARGET_FILE"
else
    echo "Property 'output_filename' not found. Checking for other schema violations."
fi

echo -e "\n=== [2/3] Smoking-Gun Audit: Source File Content ==="
# Display content with line numbers to pinpoint exactly where the key resides
cat -n "$TARGET_FILE"

echo -e "\n=== [3/3] Reference Audit: Schema Constraints ==="
# Show the schema to verify why it is invalid
cat -n "$SCHEMA_FILE"

echo -e "\n--- Diagnostic Complete ---"
echo "To repair this configuration, you can apply one of the sed commands below:"

# AUTOMATED REPAIRS (Commented out as requested):
# -----------------------------------------------------------------------------
# Use this command to remove the 'output_filename' line and any trailing comma if necessary
# # sed -i '/"output_filename":/d' "$TARGET_FILE"

# If the file format requires fixing the comma on the previous line after deletion:
# # sed -i -e '/"output_filename":/d' -e 's/,$/ /' "$TARGET_FILE"
# -----------------------------------------------------------------------------