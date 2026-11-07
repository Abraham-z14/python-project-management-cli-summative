import argparse

from services.ai_client import OllamaAIClient
from services.project_manager import ProjectManager
from services.storage_service import StorageService
from utils.formatters import (
    show_ai_summary,
    show_error,
    show_info,
    show_projects,
    show_success,
    show_tasks,
    show_users,
)


def build_parser():
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Manage users, projects, and tasks from the command line."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
    )

    # User commands
    add_user = subparsers.add_parser(
        "add-user",
        help="Create a new user.",
    )
    add_user.add_argument(
        "--name",
        required=True,
        help="User name.",
    )
    add_user.add_argument(
        "--email",
        required=True,
        help="User email address.",
    )

    subparsers.add_parser(
        "list-users",
        help="List all users.",
    )

    # Project commands
    add_project = subparsers.add_parser(
        "add-project",
        help="Create a project for an existing user.",
    )
    add_project.add_argument(
        "--user",
        required=True,
        help="Name of the project owner.",
    )
    add_project.add_argument(
        "--title",
        required=True,
        help="Project title.",
    )
    add_project.add_argument(
        "--description",
        default="",
        help="Project description.",
    )
    add_project.add_argument(
        "--due-date",
        help="Optional project due date.",
    )

    update_project = subparsers.add_parser(
        "update-project",
        help="Update an existing project.",
    )
    update_project.add_argument(
        "--project",
        required=True,
        help="Current project title.",
    )
    update_project.add_argument(
        "--new-title",
        help="Replacement project title.",
    )
    update_project.add_argument(
        "--description",
        help="Replacement project description.",
    )
    update_project.add_argument(
        "--due-date",
        help="Replacement due date.",
    )

    list_projects = subparsers.add_parser(
        "list-projects",
        help="List all projects or projects for one user.",
    )
    list_projects.add_argument(
        "--user",
        help="Optional user name.",
    )

    # Task commands
    add_task = subparsers.add_parser(
        "add-task",
        help="Create a task in an existing project.",
    )
    add_task.add_argument(
        "--project",
        required=True,
        help="Project title.",
    )
    add_task.add_argument(
        "--title",
        required=True,
        help="Task title.",
    )
    add_task.add_argument(
        "--assigned-to",
        help="Optional primary assignee.",
    )
    add_task.add_argument(
        "--contributor",
        action="append",
        dest="contributors",
        help=(
            "Optional contributor. "
            "Use this option multiple times for multiple contributors."
        ),
    )

    update_task = subparsers.add_parser(
        "update-task",
        help="Update an existing task.",
    )
    update_task.add_argument(
        "--project",
        required=True,
        help="Project title.",
    )
    update_task.add_argument(
        "--task",
        required=True,
        help="Current task title.",
    )
    update_task.add_argument(
        "--new-title",
        help="Replacement task title.",
    )
    update_task.add_argument(
        "--assigned-to",
        help="Replacement assignee.",
    )
    update_task.add_argument(
        "--status",
        choices=["pending", "completed"],
        help="Replacement task status.",
    )

    complete_task = subparsers.add_parser(
        "complete-task",
        help="Mark a task as completed.",
    )
    complete_task.add_argument(
        "--project",
        required=True,
        help="Project title.",
    )
    complete_task.add_argument(
        "--task",
        required=True,
        help="Task title.",
    )

    add_contributor = subparsers.add_parser(
        "add-contributor",
        help="Add a contributor to a task.",
    )
    add_contributor.add_argument(
        "--project",
        required=True,
        help="Project title.",
    )
    add_contributor.add_argument(
        "--task",
        required=True,
        help="Task title.",
    )
    add_contributor.add_argument(
        "--name",
        required=True,
        help="Contributor name.",
    )

    list_tasks = subparsers.add_parser(
        "list-tasks",
        help="List tasks belonging to a project.",
    )
    list_tasks.add_argument(
        "--project",
        required=True,
        help="Project title.",
    )

    # AI command
    summarize_project = subparsers.add_parser(
        "summarize-project",
        help="Generate an AI-assisted project summary.",
    )
    summarize_project.add_argument(
        "--project",
        required=True,
        help="Project title.",
    )

    return parser


def create_manager():
    """Create the application services and project manager."""
    storage = StorageService("data/project_data.json")
    ai_client = OllamaAIClient(model_name="llama3.2")

    return ProjectManager(
        storage=storage,
        ai_client=ai_client,
    )


def handle_command(args, manager):
    """Route parsed CLI arguments to the appropriate application action."""
    if args.command == "add-user":
        user = manager.add_user(
            args.name,
            args.email,
        )
        show_success(
            f"Created user '{user.name}'."
        )

    elif args.command == "list-users":
        show_users(
            manager.list_users()
        )

    elif args.command == "add-project":
        project = manager.add_project(
            args.user,
            args.title,
            args.description,
            args.due_date,
        )
        show_success(
            f"Created project '{project.title}' "
            f"for '{args.user}'."
        )

    elif args.command == "update-project":
        project = manager.update_project(
            args.project,
            new_title=args.new_title,
            description=args.description,
            due_date=args.due_date,
        )
        show_success(
            f"Updated project '{project.title}'."
        )

    elif args.command == "list-projects":
        projects = manager.list_projects(
            args.user
        )
        show_projects(
            projects,
            manager,
        )

    elif args.command == "add-task":
        task = manager.add_task(
            args.project,
            args.title,
            assigned_to=args.assigned_to,
            contributors=args.contributors,
        )
        show_success(
            f"Created task '{task.title}' "
            f"in project '{args.project}'."
        )

    elif args.command == "update-task":
        task = manager.update_task(
            args.project,
            args.task,
            new_title=args.new_title,
            assigned_to=args.assigned_to,
            status=args.status,
        )
        show_success(
            f"Updated task '{task.title}'."
        )

    elif args.command == "complete-task":
        task = manager.complete_task(
            args.project,
            args.task,
        )
        show_success(
            f"Completed task '{task.title}'."
        )

    elif args.command == "add-contributor":
        task = manager.add_contributor(
            args.project,
            args.task,
            args.name,
        )
        show_success(
            f"Added '{args.name}' to task '{task.title}'."
        )

    elif args.command == "list-tasks":
        tasks = manager.list_tasks(
            args.project
        )
        show_tasks(
            tasks,
            args.project,
        )

    elif args.command == "summarize-project":
        show_info(
            f"Generating AI summary for '{args.project}'..."
        )

        summary = manager.summarize_project(
            args.project
        )

        show_ai_summary(
            args.project,
            summary,
        )


def main():
    """Run the Project Management CLI."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        manager = create_manager()
        handle_command(args, manager)

    except (ValueError, TypeError, RuntimeError) as error:
        show_error(str(error))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())