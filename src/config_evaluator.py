# src/config_evaluator.py

import os
from .interfaces.config_evaluator_interface import ConfigEvaluatorInterface


class ConfigEvaluator(ConfigEvaluatorInterface):
    """
    Concrete implementation of ConfigEvaluatorInterface.

    Evaluates conditional‑execution rules defined in the Schema‑Merger‑Splitter
    Config Schema. This class performs only the structural checks required by
    the frozen Constitution:

    - All files listed in 'requires_all' must exist.
    - No file listed in 'requires_none' may exist.

    Missing fields are structural violations and must raise errors.
    """

    def evaluate_run_conditions(self, config_run_entry):
        """
        Return True if:
            - every file in 'requires_all' exists
            - no file in 'requires_none' exists

        Return False otherwise.

        Missing fields are structural errors and must raise exceptions.
        """

        # --- Required fields must exist ---
        if "requires_all" not in config_run_entry:
            raise ValueError("Config entry missing required field: 'requires_all'")

        if "requires_none" not in config_run_entry:
            raise ValueError("Config entry missing required field: 'requires_none'")

        requires_all = config_run_entry["requires_all"]
        requires_none = config_run_entry["requires_none"]

        # --- Type checks (structural, not optional) ---
        if not isinstance(requires_all, list):
            raise TypeError("'requires_all' must be a list")

        if not isinstance(requires_none, list):
            raise TypeError("'requires_none' must be a list")

        # --- File existence checks ---
        for path in requires_all:
            if not os.path.exists(path):
                return False

        for path in requires_none:
            if os.path.exists(path):
                return False

        return True