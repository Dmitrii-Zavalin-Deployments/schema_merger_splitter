# tests/dummies/results_object_dummy.py

import logging
from src.interfaces.orchestrator_interface import SchemaMergerSplitterOrchestratorInterface

logger = logging.getLogger(__name__)

class ResultsObjectDummy(SchemaMergerSplitterOrchestratorInterface):
    """
    Dummy representation of the results object and orchestrator behavior
    for the Schema‑Merger‑Splitter module.

    Used exclusively during Phase 6 — Implementation Quality Gates.

    This dummy:
    - inherits from SchemaMergerSplitterOrchestratorInterface,
    - contains no logic,
    - stores all fields as attributes,
    - provides deterministic override semantics,
    - satisfies all Phase‑1 Results Schema requirements.
    """

    def __init__(self):
        # Deterministic, schema‑valid baseline values
        self.success = False
        self.errors = []

    def override(self, **kwargs):
        """
        Deterministically override fields for scenario and edge‑case testing.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    # ----------------------------------------------------------------------
    # Interface‑required methods (dummy implementations)
    # ----------------------------------------------------------------------

    def run(self, input_json_instance):
        logger.debug(
            "ResultsObjectDummy.run() called — Phase‑3 dummy contains no logic."
        )

    def validate_input_json(self, input_json_instance):
        logger.debug(
            "ResultsObjectDummy.validate_input_json() called — Phase‑3 dummy contains no logic."
        )

    def load_source_files(self, input_json_instance):
        logger.debug(
            "ResultsObjectDummy.load_source_files() called — Phase‑3 dummy contains no logic."
        )

    def execute_copy_operations(self, loaded_sources, input_json_instance):
        logger.debug(
            "ResultsObjectDummy.execute_copy_operations() called — Phase‑3 dummy contains no logic."
        )

    def write_merged_output(self, merged_output, input_json_instance):
        logger.debug(
            "ResultsObjectDummy.write_merged_output() called — Phase‑3 dummy contains no logic."
        )

    def write_results_json(self, success, errors, input_json_instance):
        logger.debug(
            "ResultsObjectDummy.write_results_json() called — Phase‑3 dummy contains no logic."
        )
