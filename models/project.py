from models.base import BaseEntity
from models.task import Task


class Project(BaseEntity):
    """Represents a project containing one or more tasks."""

    def __init__(
        self,
        title,
        description="",
        due_date=None,
        tasks=None,
        entity_id=None,
    ):
        """Create a project and optionally restore its tasks."""
        super().__init__(entity_id)

        self.title = title
        self.description = description
        self.due_date = due_date
        self.tasks = []

        for task in tasks or []:
            self.add_task(task)

    @property
    def title(self):
        """Return the project title."""
        return self._title

    @title.setter
    def title(self, value):
        """Validate and store the project title."""
        self._title = self.require_text(value, "Project title")

    @property
    def description(self):
        """Return the project description."""
        return self._description

    @description.setter
    def description(self, value):
        """Store a project description."""
        if value is None:
            value = ""

        if not isinstance(value, str):
            raise ValueError("Project description must be text.")

        self._description = value.strip()

    @property
    def due_date(self):
        """Return the optional due date."""
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        """Store an optional due-date string."""
        if value is None or value == "":
            self._due_date = None
            return

        self._due_date = self.require_text(value, "Due date")

    def add_task(self, task):
        """Add a Task object to the project."""
        if not isinstance(task, Task):
            raise TypeError("Project tasks must be Task objects.")

        self.tasks.append(task)

    def get_task(self, title):
        """Find a task by title, ignoring letter case."""
        cleaned = self.require_text(title, "Task title")

        for task in self.tasks:
            if task.title.lower() == cleaned.lower():
                return task

        return None

    def complete_task(self, title):
        """Find a task by title and mark it complete."""
        task = self.get_task(title)

        if task is None:
            raise ValueError(f"Task '{title}' was not found.")

        task.complete()
        return task

    def to_dict(self):
        """Convert the project and its tasks into dictionary data."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a Project and its Task objects from stored data."""
        tasks = [
            Task.from_dict(task_data)
            for task_data in data.get("tasks", [])
        ]

        return cls(
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            tasks=tasks,
            entity_id=data.get("id"),
        )

    def __str__(self):
        """Return a readable project description."""
        return f"{self.title} ({len(self.tasks)} tasks)"