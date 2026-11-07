import json

import pytest

from models import Project, Task, User
from services.storage_service import StorageService


def test_missing_file_loads_as_empty_list(tmp_path):
    storage = StorageService(tmp_path / "missing.json")

    assert storage.load_users() == []


def test_users_save_and_load(tmp_path):
    file_path = tmp_path / "project_data.json"
    storage = StorageService(file_path)

    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    task = Task("Write tests", assigned_to="Alex")

    project.add_task(task)
    user.add_project(project)

    storage.save_users([user])

    loaded = storage.load_users()

    assert len(loaded) == 1
    assert loaded[0].name == "Alex"
    assert loaded[0].projects[0].title == "CLI Tool"
    assert loaded[0].projects[0].tasks[0].title == "Write tests"


def test_saved_file_is_valid_json(tmp_path):
    file_path = tmp_path / "project_data.json"
    storage = StorageService(file_path)

    storage.save_users([
        User("Alex", "alex@example.com")
    ])

    with file_path.open(encoding="utf-8") as file:
        data = json.load(file)

    assert "users" in data
    assert data["users"][0]["name"] == "Alex"


def test_invalid_json_raises_readable_error(tmp_path):
    file_path = tmp_path / "broken.json"
    file_path.write_text("{ broken json", encoding="utf-8")

    storage = StorageService(file_path)

    with pytest.raises(
        RuntimeError,
        match="invalid JSON",
    ):
        storage.load_users()


def test_invalid_root_structure_raises_error(tmp_path):
    file_path = tmp_path / "bad_structure.json"
    file_path.write_text(
        '["not", "an", "object"]',
        encoding="utf-8",
    )

    storage = StorageService(file_path)

    with pytest.raises(
        RuntimeError,
        match="JSON object",
    ):
        storage.load_users()


def test_invalid_users_structure_raises_error(tmp_path):
    file_path = tmp_path / "bad_users.json"
    file_path.write_text(
        '{"users": "wrong"}',
        encoding="utf-8",
    )

    storage = StorageService(file_path)

    with pytest.raises(
        RuntimeError,
        match="users list",
    ):
        storage.load_users()


def test_clear_resets_saved_users(tmp_path):
    storage = StorageService(
        tmp_path / "project_data.json"
    )

    storage.save_users([
        User("Alex", "alex@example.com")
    ])

    storage.clear()

    assert storage.load_users() == []