# tests/dummies/config_run_dummy.py

from src.interfaces.config_evaluator_interface import ConfigEvaluatorInterface

class ConfigRunDummy(ConfigEvaluatorInterface):
    """
    Dummy representation of a single run entry from the Config Schema.
    Used exclusively during Phase 6 — Implementation Quality Gates.

    This dummy:
    - inherits from ConfigEvaluatorInterface,
    - contains no logic,
    - stores all fields as attributes,
    - provides deterministic override semantics,
    - satisfies all Phase‑1 schema requirements.
    """

    def __init__(self):
        # Deterministic, schema‑valid baseline values
        self.requires_all = []
        self.requires_none = []
        self.input_file = ""

    def override(self, **kwargs):
        """
        Deterministically override fields for scenario and edge‑case testing.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def evaluate_run_conditions(self, config_run_entry):
        """
        Required by ConfigEvaluatorInterface.
        Dummy implementation — contains no logic.
        """
        raise NotImplementedError