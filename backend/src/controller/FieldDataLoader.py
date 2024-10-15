class FieldDataLoader:
    """Abstract class responsible for loading field data."""

    def load_data(self, source):
        raise NotImplementedError("Subclasses should implement this method.")
