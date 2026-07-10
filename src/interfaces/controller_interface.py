class SchemaMergerSplitterControllerInterface:
    """
    Contract‑only interface for the Schema‑Merger‑Splitter controller.
    This controller performs Step 2 of the Minimal Step Path:

        Step 2 — Load the merger‑splitter input file

    No logic, no defaults, and no computations may appear in this interface.
    Subclasses must not define any additional methods or attributes.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        ALLOWED_MEMBERS = {
            "load_input_file"
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
    # Step 2 — Load the merger‑splitter input file
    # ------------------------------------------------------------
    def load_input_file(self, input_file_path):
        """
        Load the merger‑splitter input JSON referenced by input_file_path.

        Returns:
            output_filename: str
            sources: dict mapping source filenames → list of {from, to} rules
        """
        raise NotImplementedError