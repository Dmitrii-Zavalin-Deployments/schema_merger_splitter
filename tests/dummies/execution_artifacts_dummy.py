class ExecutionArtifactsDummy(dict):
    """
    Test‑only dummy representing the Schema‑Merger‑Splitter execution artifacts.

    This dummy simulates the input, config, and results data structures
    that flow through the controller → orchestrator → assembler pipeline.

    It contains no production logic and is used exclusively during
    Phase 6 — Implementation Quality Gates for deterministic scenario
    and edge‑case testing.

    Primary fields (dict keys):
        - inputs:  dict matching schema_merger_splitter_input_schema.json
        - config:  dict matching schema_merger_splitter_config_schema.json
        - results: dict matching schema_merger_splitter_results_schema.json

    Secondary testing metadata (instance attributes):
        - scenario_label
        - injected_error

    The dummy provides deterministic override semantics to allow tests
    to mutate state predictably without invoking production logic.
    """

    def __init__(self):
        # 1. Initialize primary fields as dict keys using schema‑valid defaults
        super().__init__({
            "inputs": {
                "output_filename": "",
                "sources": {}
            },
            "config": {
                "runs": []
            },
            "results": {
                "success": False,
                "errors": []
            }
        })

        # 2. Secondary fields stored as attributes
        self.scenario_label = None
        self.injected_error = None

    def override(self, **kwargs):
        """
        Overrides primary fields in the dict and secondary fields
        as attributes. This ensures deterministic mutation semantics
        across all tests.
        """
        primary_fields = {"inputs", "config", "results"}

        for key, value in kwargs.items():
            if key in primary_fields:
                self[key] = value
            else:
                setattr(self, key, value)

        return self