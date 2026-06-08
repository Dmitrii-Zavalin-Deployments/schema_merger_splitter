class SchemaMergerSplitterOrchestratorInterface:
    """
    Contract‑only interface for the Schema‑Merger‑Splitter orchestrator.
    Defines the deterministic sequence of structural operations required
    to execute the minimal step path described in Section 2.2.

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
        }

        for name in cls.__dict__:
            if name.startswith("__"):
                continue
            if name not in ALLOWED_MEMBERS:
                raise TypeError(
                    f"CONSTITUTION VIOLATION: Subclass '{cls.__name__}' is strictly "
                    f"prohibited from defining custom member '{name}'. "
                    f"Allowed interface members are: {ALLOWED_MEMBERS}"
                )

    def run(self, input_json_instance):
        """
        Execute the full Schema‑Merger‑Splitter minimal step path.
        """
        raise NotImplementedError

    def validate_input_json(self, input_json_instance):
        """
        Validate the input JSON against the Input Schema.
        Reject missing fields, incorrect types, or extra fields.
        """
        raise NotImplementedError

    def load_source_files(self, input_json_instance):
        """
        Load all source files from data/testing-input-output/.
        Missing or unreadable files must be recorded as errors.
        """
        raise NotImplementedError

    def execute_copy_operations(self, loaded_sources, input_json_instance):
        """
        Execute one copy operation per mapping:
        - Evaluate JSONPath
        - Detect missing fields
        - Detect duplicate 'to' keys
        - Insert extracted values into the merged output object
        """
        raise NotImplementedError

    def write_merged_output(self, merged_output, input_json_instance):
        """
        Write the merged output file to data/testing-input-output/<output_filename>
        only if no errors occurred.
        """
        raise NotImplementedError

    def write_results_json(self, success, errors, input_json_instance):
        """
        Always write the results JSON containing:
        - success: bool
        - errors: list of strings
        """
        raise NotImplementedError
