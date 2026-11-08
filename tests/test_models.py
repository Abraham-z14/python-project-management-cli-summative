import pytest

from models import BaseEntity, Project, Task, User


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset model IDs so tests remain predictable."""
    User._next_id = 1
    Project._next_id = 1
    Task._next_id = 1
    yield


def test_user_creation():
    user = User("Alex", "alex@example.com")

    assert user.id == 1
    assert user.name == "Alex"
    assert user.email == "alex@example.com"
    assert user.projects == []


def test_user_rejects_invalid_email():
    with pytest.raises(ValueError, match="valid email"):
        User("Alex", "not-an-email")


def test_user_adds_project():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")

    user.add_project(project)

    assert user.projects == [project]


def test_user_rejects_non_project():
    user = User("Alex", "alex@example.com")

    with pytest.raises(TypeError, match="Project objects"):
        user.add_project("not a project")


def test_project_adds_task():
    project = Project("CLI Tool")
    task = Task("Write tests")

    project.add_task(task)

    assert project.tasks == [task]


def test_project_finds_task_case_insensitively():
    project = Project("CLI Tool")
    task = Task("Write Tests")
    project.add_task(task)

    assert project.get_task("write tests") is task


def test_project_completes_task():
    project = Project("CLI Tool")
    task = Task("Write tests")
    project.add_task(task)

    result = project.complete_task("Write tests")

    assert result is task
    assert task.status == "completed"


def test_project_missing_task_raises_error():
    project = Project("CLI Tool")

    with pytest.raises(ValueError, match="was not found"):
        project.complete_task("Missing task")


def test_task_rejects_invalid_status():
    with pytest.raises(ValueError, match="pending or completed"):
        Task("Write tests", status="broken")


def test_task_adds_unique_contributors():
    task = Task("Write tests")

    task.add_contributor("Alex")
    task.add_contributor("Alex")
    task.add_contributor("Maya")

    assert task.contributors == ["Alex", "Maya"]


def test_task_complete_changes_status():
    task = Task("Write tests")

    task.complete()

    assert task.status == "completed"


def test_nested_objects_round_trip_through_dicts():
    task = Task(
        "Write tests",
        assigned_to="Alex",
        contributors=["Maya"],
    )

    project = Project(
        "CLI Tool",
        description="Build a CLI",
        due_date="2026-12-01",
        tasks=[task],
    )

    user = User(
        "Alex",
        "alex@example.com",
        projects=[project],
    )

    restored = User.from_dict(user.to_dict())

    assert restored.name == "Alex"
    assert restored.projects[0].title == "CLI Tool"
    assert restored.projects[0].tasks[0].title == "Write tests"
    assert restored.projects[0].tasks[0].contributors == ["Maya"]


def test_string_methods_are_readable():
    user = User("Alex", "alex@example.com")
    project = Project("CLI Tool")
    task = Task("Write tests", assigned_to="Alex")

    assert "Alex" in str(user)
    assert "CLI Tool" in str(project)
    assert "Write tests" in str(task)