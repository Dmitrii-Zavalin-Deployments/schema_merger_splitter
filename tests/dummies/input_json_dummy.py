# tests/dummies/input_json_dummy.py

import logging
from src.interfaces.input_loader_interface import InputLoaderInterface

logger = logging.getLogger(__name__)

class InputJsonDummy(InputLoaderInterface):
    """
    Dummy representation of a validated merger‑splitter input JSON file.
    Used exclusively during Phase 6 — Implementation Quality Gates.

    This dummy:
    - inherits from InputLoaderInterface,
    - contains no logic,
    - stores all fields as attributes,
    - provides deterministic override semantics,
    - satisfies all Phase‑1 Input Schema requirements.
    """

    def __init__(self):
        # Deterministic, schema‑valid baseline values
        # These match the Input Schema exactly.
        self.sources = {}          # mapping: filename -> list of {from, to}
        self.output_filename = ""  # required string

    def override(self, **kwargs):
        """
        Deterministically override fields for scenario and edge‑case testing.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def load_and_validate_input(self, input_file_path):
        """
        Required by InputLoaderInterface.
        Dummy implementation — contains no logic and must not be executed.
        """
        logger.debug(
            "InputJsonDummy.load_and_validate_input() called — "
            "Phase‑3 dummy contains no logic."
        )
