import json
from pathlib import Path

from models import User


class StorageService:
    """Handles saving and loading project-management data as JSON."""

    def __init__(self, file_path="data/project_data.json"):
        """Store the location of the JSON data file."""
        self.file_path = Path(file_path)

    def save_users(self, users):
        """Save a collection of User objects to the JSON file."""
        if not isinstance(users, list):
            raise TypeError("users must be provided as a list.")

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "users": [user.to_dict() for user in users]
        }

        try:
            with self.file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        except OSError as error:
            raise RuntimeError(
                f"Could not save project data: {error}"
            ) from error

    def load_users(self):
        """Load User objects and their nested projects/tasks from JSON."""
        if not self.file_path.exists():
            return []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Project data file contains invalid JSON."
            ) from error

        except OSError as error:
            raise RuntimeError(
                f"Could not load project data: {error}"
            ) from error

        if not isinstance(data, dict):
            raise RuntimeError(
                "Project data file must contain a JSON object."
            )

        users_data = data.get("users", [])

        if not isinstance(users_data, list):
            raise RuntimeError(
                "Project data must contain a users list."
            )

        return [
            User.from_dict(user_data)
            for user_data in users_data
        ]

    def clear(self):
        """Reset the stored application data."""
        self.save_users([])