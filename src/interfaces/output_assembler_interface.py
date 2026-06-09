class SchemaMergerSplitterOutputAssemblerInterface:
    """
    Contract‑only interface for assembling the final output object for a single run.

    This interface corresponds to Step 7 of the Minimal Step Path:

        - Receive execution artifacts from the orchestrator
        - Validate them against the frozen Output Schema
        - Write the final assembled output file to output_assembler_file

    No logic, no defaults, and no computations may appear in this interface.
    Subclasses must not define any additional methods or attributes.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        ALLOWED_MEMBERS = {
            "assemble_final_output"
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
    # Step 7 — Assemble final output object
    # ------------------------------------------------------------
    def assemble_final_output(self, inputs, config, results, output_assembler_file):
        """
        Assemble the final output object:

            {
                "inputs":  <validated input JSON instance>,
                "config":  <validated config entry>,
                "results": <results JSON instance>
            }

        Validate this object against the frozen Output Schema and write it
        to the file specified by output_assembler_file.

        Parameters:
            inputs: dict
            config: dict
            results: dict
            output_assembler_file: str

        Returns:
            None
        """
        raise NotImplementedError