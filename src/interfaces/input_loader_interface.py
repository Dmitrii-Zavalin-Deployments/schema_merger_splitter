class InputLoaderInterface:
    """
    Contract‑only interface for loading and validating the merger‑splitter
    input JSON for an activated run.

    No logic, no defaults, and no computations may appear in this interface.
    Subclasses must not define any additional methods or attributes.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        ALLOWED_MEMBERS = {"load_and_validate_input"}

        for name in cls.__dict__:
            if name.startswith("__"):
                continue
            if name not in ALLOWED_MEMBERS:
                raise TypeError(
                    f"CONSTITUTION VIOLATION: Subclass '{cls.__name__}' "
                    f"may not define custom member '{name}'. "
                    f"Allowed members: {ALLOWED_MEMBERS}"
                )

    def load_and_validate_input(self, input_file_path):
        """
        Load the input JSON file and validate it against the Input Schema.
        Return the parsed JSON instance.
        """
        raise NotImplementedError