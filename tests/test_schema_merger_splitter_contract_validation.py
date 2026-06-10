# tests/test_schema_merger_splitter_contract_validation.py

import json
from pathlib import Path
import pytest
from jsonschema import validate, ValidationError

from tests.signatures.schema_merger_splitter_contract_validation import (
    SchemaMergerSplitterContractValidation,
)
from tests.dummies.execution_artifacts_dummy import ExecutionArtifactsDummy


class TestSchemaMergerSplitterContractValidation(SchemaMergerSplitterContractValidation):
    """
    Concrete Phase‑6 implementation of schema‑level validation tests.
    Ensures Input Schema and Results Schema behave exactly as required.
    """

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------

    def _load_schema(self, name: str):
        schema_path = Path("schema") / name
        with schema_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------
    # Input Schema Tests
    # ------------------------------------------------------------

    def test_input_type_validation(self):
        schema = self._load_schema("schema_merger_splitter_input_schema.json")

        # Valid input
        valid = {
            "output_filename": "x.json",
            "sources": {},
        }
        validate(instance=valid, schema=schema)

        # Wrong type for output_filename
        invalid = {
            "output_filename": 123,  # must be string
            "sources": {},
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid, schema=schema)

    def test_input_presence_validation(self):
        schema = self._load_schema("schema_merger_splitter_input_schema.json")

        # Missing required field: output_filename
        missing = {
            "sources": {},
        }
        with pytest.raises(ValidationError):
            validate(instance=missing, schema=schema)

        # Missing required field: sources
        missing2 = {
            "output_filename": "x.json",
        }
        with pytest.raises(ValidationError):
            validate(instance=missing2, schema=schema)

    def test_input_excess_field_validation(self):
        schema = self._load_schema("schema_merger_splitter_input_schema.json")

        # Extra field not allowed
        invalid = {
            "output_filename": "x.json",
            "sources": {},
            "extra": 123,
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid, schema=schema)

    # ------------------------------------------------------------
    # Results Schema Tests
    # ------------------------------------------------------------

    def test_results_type_validation(self):
        schema = self._load_schema("schema_merger_splitter_results_schema.json")

        # Valid
        valid = {"success": True, "errors": []}
        validate(instance=valid, schema=schema)

        # Wrong type for success
        invalid = {"success": "yes", "errors": []}
        with pytest.raises(ValidationError):
            validate(instance=invalid, schema=schema)

        # Wrong type for errors
        invalid2 = {"success": True, "errors": "not a list"}
        with pytest.raises(ValidationError):
            validate(instance=invalid2, schema=schema)

    def test_results_presence_validation(self):
        schema = self._load_schema("schema_merger_splitter_results_schema.json")

        # Missing success
        missing = {"errors": []}
        with pytest.raises(ValidationError):
            validate(instance=missing, schema=schema)

        # Missing errors
        missing2 = {"success": True}
        with pytest.raises(ValidationError):
            validate(instance=missing2, schema=schema)

    def test_results_excess_field_validation(self):
        schema = self._load_schema("schema_merger_splitter_results_schema.json")

        # Extra field not allowed
        invalid = {
            "success": True,
            "errors": [],
            "extra": "nope",
        }
        with pytest.raises(ValidationError):
            validate(instance=invalid, schema=schema)