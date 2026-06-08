class ConfigEvaluatorInterface:
    """
    Contract‑only interface for evaluating conditional‑execution rules
    defined in the Schema‑Merger‑Splitter Config Schema.

    No logic, no defaults, and no computations may appear in this interface.
    Subclasses must not define any additional methods or attributes.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        ALLOWED_MEMBERS = {"evaluate_run_conditions"}

        for name in cls.__dict__:
            if name.startswith("__"):
                continue
            if name not in ALLOWED_MEMBERS:
                raise TypeError(
                    f"CONSTITUTION VIOLATION: Subclass '{cls.__name__}' "
                    f"may not define custom member '{name}'. "
                    f"Allowed members: {ALLOWED_MEMBERS}"
                )

    def evaluate_run_conditions(self, config_run_entry):
        """
        Given a single run entry from the Config Schema, return:
        - True if all 'requires_all' files exist AND all 'requires_none' files do not exist
        - False otherwise
        """
        raise NotImplementedError