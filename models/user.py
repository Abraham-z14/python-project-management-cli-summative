from models.base import BaseEntity
from models.project import Project


class User(BaseEntity):
    """Represents a user who owns one or more projects."""

    def __init__(self, name, email, projects=None, entity_id=None):
        """Create a user and optionally restore owned projects."""
        super().__init__(entity_id)

        self.name = name
        self.email = email
        self.projects = []

        for project in projects or []:
            self.add_project(project)

    @property
    def name(self):
        """Return the user's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Validate and store the user's name."""
        self._name = self.require_text(value, "User name")

    @property
    def email(self):
        """Return the user's email address."""
        return self._email

    @email.setter
    def email(self, value):
        """Validate and store a basic email address."""
        cleaned = self.require_text(value, "Email")

        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("Email must be a valid email address.")

        self._email = cleaned

    def add_project(self, project):
        """Associate a Project object with the user."""
        if not isinstance(project, Project):
            raise TypeError("User projects must be Project objects.")

        self.projects.append(project)

    def get_project(self, title):
        """Find one of the user's projects by title."""
        cleaned = self.require_text(title, "Project title")

        for project in self.projects:
            if project.title.lower() == cleaned.lower():
                return project

        return None

    def to_dict(self):
        """Convert the user and projects into dictionary data."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "projects": [
                project.to_dict()
                for project in self.projects
            ],
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a User and associated projects from stored data."""
        projects = [
            Project.from_dict(project_data)
            for project_data in data.get("projects", [])
        ]

        return cls(
            name=data["name"],
            email=data["email"],
            projects=projects,
            entity_id=data.get("id"),
        )

    def __str__(self):
        """Return a readable user description."""
        return f"{self.name} <{self.email}>"