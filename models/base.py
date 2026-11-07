class BaseEntity:
    """Base class that provides shared ID and validation behavior."""

    _next_id = 1

    def __init__(self, entity_id=None):
        """Assign a unique integer ID or restore an existing ID."""
        cls = type(self)

        if entity_id is None:
            self.id = cls._next_id
            cls._next_id += 1
        else:
            self.id = int(entity_id)
            cls._next_id = max(cls._next_id, self.id + 1)

    @staticmethod
    def require_text(value, field_name):
        """Validate and clean required text values."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")

        return value.strip()