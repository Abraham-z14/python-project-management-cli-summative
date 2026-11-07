from models.base import BaseEntity


class Task(BaseEntity):
    """Represents a task belonging to a project."""

    VALID_STATUSES = {"pending", "completed"}

    def __init__(
        self,
        title,
        assigned_to=None,
        status="pending",
        contributors=None,
        entity_id=None,
    ):
        """Create a task with assignment, status, and contributor data."""
        super().__init__(entity_id)

        self.title = title
        self.assigned_to = assigned_to
        self.status = status
        self.contributors = []

        for contributor in contributors or []:
            self.add_contributor(contributor)

    @property
    def title(self):
        """Return the task title."""
        return self._title

    @title.setter
    def title(self, value):
        """Validate and store the task title."""
        self._title = self.require_text(value, "Task title")

    @property
    def assigned_to(self):
        """Return the primary assignee."""
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, value):
        """Store an optional assignee name."""
        if value is None or value == "":
            self._assigned_to = None
            return

        self._assigned_to = self.require_text(value, "Assigned user")

    @property
    def status(self):
        """Return the current task status."""
        return self._status

    @status.setter
    def status(self, value):
        """Restrict task status to supported values."""
        if not isinstance(value, str):
            raise ValueError("Task status must be text.")

        cleaned = value.strip().lower()

        if cleaned not in self.VALID_STATUSES:
            raise ValueError("Task status must be pending or completed.")

        self._status = cleaned

    def complete(self):
        """Mark the task as completed."""
        self.status = "completed"

    def add_contributor(self, contributor):
        """Add a contributor without creating duplicates."""
        cleaned = self.require_text(contributor, "Contributor")

        if cleaned not in self.contributors:
            self.contributors.append(cleaned)

    def to_dict(self):
        """Convert the task into JSON-serializable data."""
        return {
            "id": self.id,
            "title": self.title,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "contributors": list(self.contributors),
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Task object from stored dictionary data."""
        return cls(
            title=data["title"],
            assigned_to=data.get("assigned_to"),
            status=data.get("status", "pending"),
            contributors=data.get("contributors", []),
            entity_id=data.get("id"),
        )

    def __str__(self):
        """Return a readable task description for CLI output."""
        marker = "✓" if self.status == "completed" else "○"
        assignee = self.assigned_to or "Unassigned"

        return f"{marker} {self.title} [{assignee}]"