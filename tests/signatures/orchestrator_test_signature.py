class SchemaMergerSplitterOrchestratorTestSignature:
    """
    Contract‑level signature for the Schema‑Merger‑Splitter orchestrator.
    No logic, no assertions, no execution.
    Defines the required behavioural and edge‑case validation responsibilities.
    """

    def test_validate_input_json(self):
        """
        Input JSON must match the Input Schema exactly.
        Missing fields, extra fields, or incorrect types must cause failure.
        """
        raise NotImplementedError

    def test_load_source_files(self):
        """
        All source files must be loaded from data/testing-input-output/.
        Missing or unreadable files must be reported as errors.
        """
        raise NotImplementedError

    def test_execute_copy_operations(self):
        """
        Each mapping must:
        - extract the JSONPath value,
        - detect missing fields,
        - detect duplicate 'to' keys,
        - insert the value into the merged output.
        """
        raise NotImplementedError

    def test_write_merged_output(self):
        """
        The merged output file must be written only if no errors occurred.
        """
        raise NotImplementedError

    def test_write_results_json(self):
        """
        The results JSON must always be written and must contain:
        - success: bool
        - errors: list of strings
        """
        raise NotImplementedError

    def test_pipeline_end_to_end(self):
        """
        End‑to‑end behaviour:
        - valid input produces a merged file and success=true,
        - invalid input produces no merged file and success=false.
        """
        raise NotImplementedError
