class SchemaMergerSplitterOrchestratorInterface:
    """
    Contract‑only interface for executing the Schema‑Merger‑Splitter Minimal Step Path
    for a single activated run.

    No logic, no defaults, and no computations may appear in this interface.
    Subclasses must not define any additional methods or attributes.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        ALLOWED_MEMBERS = {
            "run",
            "validate_input_json",
            "load_source_files",
            "execute_copy_operations",
            "write_merged_output",
            "write_results_json",
            "get_execution_artifacts",
        }

        for name in cls.__dict__:
            if name.startswith("__"):
                continue
            if name not in ALLOWED_MEMBERS:
                raise TypeError(
                    f"CONSTITUTION VIOLATION: Subclass '{cls.__name__}' "
                    f"may not define custom member '{name}'. "
                    f"Allowed members: {ALLOWED_MEMBERS}"
                )

    # ------------------------------------------------------------
    # Step 2 (partially): Validate input JSON
    # ------------------------------------------------------------
    def validate_input_json(self, input_json_instance):
        """
        Validate the input JSON against the Input Schema.
        Must detect:
        - missing required fields
        - extra fields
        - incorrect types
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Step 3: Load all source JSON files
    # ------------------------------------------------------------
    def load_source_files(self, input_json_instance):
        """
        Load all source files referenced in input_json_instance["sources"].

        Returns:
            loaded_sources: dict of filename → loaded JSON
            errors: list of error messages
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Step 4: Execute copy operations
    # ------------------------------------------------------------
    def execute_copy_operations(self, loaded_sources, input_json_instance):
        """
        Execute one copy operation per mapping:
        - Evaluate JSONPath
        - Detect missing fields
        - Detect duplicate 'to' keys
        - Insert extracted values into the merged output object

        Returns:
            merged_output: dict
            errors: list of error messages
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Step 5: Write merged output file
    # ------------------------------------------------------------
    def write_merged_output(self, merged_output, input_json_instance):
        """
        Write the merged output file to:
            data/testing-input-output/<output_filename>

        Only executed if no fatal errors occurred.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Step 6: Write results JSON
    # ------------------------------------------------------------
    def write_results_json(self, success, errors, input_json_instance):
        """
        Always write the results JSON containing:
            {
                "success": <bool>,
                "errors": <list of strings>
            }
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Step 7 (assembler uses this): Expose execution artifacts
    # ------------------------------------------------------------
    def get_execution_artifacts(self):
        """
        Return the validated input JSON, the validated config JSON,
        and the results object.

        Required for Phase 5 Output Assembly.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    # Full Minimal Step Path executor
    # ------------------------------------------------------------
    def run(self, input_json_instance):
        """
        Execute the full Minimal Step Path for a single run.
        """
        raise NotImplementedError