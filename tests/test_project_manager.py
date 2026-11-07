import pytest

from services.project_manager import ProjectManager
from services.storage_service import StorageService


class FakeAIClient:
    """Small fake service used to test AI integration safely."""

    def __init__(self):
        self.last_prompt = None

    def send(self, prompt):
        self.last_prompt = prompt
        return "Generated project summary."


@pytest.fixture
def manager(tmp_path):
    storage = StorageService(
        tmp_path / "project_data.json"
    )

    return ProjectManager(
        storage,
        FakeAIClient(),
    )


def test_add_user(manager):
    user = manager.add_user(
        "Alex",
        "alex@example.com",
    )

    assert user.name == "Alex"
    assert manager.find_user("alex") is user


def test_duplicate_user_is_rejected(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        manager.add_user(
            "Alex",
            "another@example.com",
        )


def test_duplicate_email_is_rejected(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )

    with pytest.raises(
        ValueError,
        match="already in use",
    ):
        manager.add_user(
            "Jordan",
            "alex@example.com",
        )


def test_add_project_to_user(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )

    project = manager.add_project(
        "Alex",
        "CLI Tool",
        "Build a project manager",
        "2026-12-01",
    )

    assert project.title == "CLI Tool"
    assert manager.find_project("cli tool") is project


def test_project_requires_existing_user(manager):
    with pytest.raises(
        ValueError,
        match="not found",
    ):
        manager.add_project(
            "Missing",
            "CLI Tool",
        )


def test_update_project(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )

    project = manager.update_project(
        "CLI Tool",
        new_title="Project CLI",
        description="Updated description",
        due_date="2026-12-20",
    )

    assert project.title == "Project CLI"
    assert project.description == "Updated description"
    assert project.due_date == "2026-12-20"


def test_add_task(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )

    task = manager.add_task(
        "CLI Tool",
        "Write tests",
        assigned_to="Alex",
        contributors=["Maya"],
    )

    assert task.title == "Write tests"
    assert task.assigned_to == "Alex"
    assert task.contributors == ["Maya"]


def test_duplicate_task_is_rejected(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )
    manager.add_task(
        "CLI Tool",
        "Write tests",
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        manager.add_task(
            "CLI Tool",
            "write tests",
        )


def test_update_task(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )
    manager.add_task(
        "CLI Tool",
        "Write tests",
    )

    task = manager.update_task(
        "CLI Tool",
        "Write tests",
        new_title="Complete tests",
        assigned_to="Alex",
        status="completed",
    )

    assert task.title == "Complete tests"
    assert task.assigned_to == "Alex"
    assert task.status == "completed"


def test_complete_task(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )
    manager.add_task(
        "CLI Tool",
        "Write tests",
    )

    task = manager.complete_task(
        "CLI Tool",
        "Write tests",
    )

    assert task.status == "completed"


def test_add_contributor(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )
    manager.add_task(
        "CLI Tool",
        "Write tests",
    )

    task = manager.add_contributor(
        "CLI Tool",
        "Write tests",
        "Maya",
    )

    assert task.contributors == ["Maya"]


def test_changes_persist_to_storage(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )
    manager.add_project(
        "Alex",
        "CLI Tool",
    )
    manager.add_task(
        "CLI Tool",
        "Write tests",
    )

    reloaded = ProjectManager(
        manager.storage
    )

    assert reloaded.find_user("Alex") is not None
    assert reloaded.find_project("CLI Tool") is not None
    assert (
        reloaded
        .find_project("CLI Tool")
        .get_task("Write tests")
        is not None
    )


def test_ai_summary_uses_project_data(manager):
    manager.add_user(
        "Alex",
        "alex@example.com",
    )

    manager.add_project(
        "Alex",
        "CLI Tool",
        "Build a project manager",
        "2026-12-01",
    )

    manager.add_task(
        "CLI Tool",
        "Write tests",
        assigned_to="Alex",
        contributors=["Maya"],
    )

    result = manager.summarize_project(
        "CLI Tool"
    )

    prompt = manager.ai_client.last_prompt

    assert result == "Generated project summary."
    assert "CLI Tool" in prompt
    assert "Build a project manager" in prompt
    assert "Write tests" in prompt
    assert "Alex" in prompt
    assert "Maya" in prompt
    assert "Do not invent" in prompt


def test_ai_summary_requires_client(tmp_path):
    manager = ProjectManager(
        StorageService(
            tmp_path / "project_data.json"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="No AI client",
    ):
        manager.summarize_project("Anything")