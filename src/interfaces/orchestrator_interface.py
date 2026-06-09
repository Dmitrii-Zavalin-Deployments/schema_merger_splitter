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

    def run(self, input_json_instance):
        """Execute the full Minimal Step Path for a single run."""
        raise NotImplementedError

    def validate_input_json(self, input_json_instance):
        """Validate the input JSON against the Input Schema."""
        raise NotImplementedError

    def load_source_files(self, input_json_instance):
        """Load all source files referenced in the input JSON."""
        raise NotImplementedError

    def execute_copy_operations(self, loaded_sources, input_json_instance):
        """Execute one copy operation per mapping."""
        raise NotImplementedError

    def write_merged_output(self, merged_output, input_json_instance):
        """Write the merged output file if no errors occurred."""
        raise NotImplementedError

    def write_results_json(self, success, errors, input_json_instance):
        """Always write the results JSON."""
        raise NotImplementedError

    def get_execution_artifacts(self):
        """
        Return the validated input JSON, the validated config JSON, and the results object.
        Required for Phase 5 Output Assembly.
        """
        raise NotImplementedError