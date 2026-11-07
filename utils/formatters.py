from rich.console import Console
from rich.table import Table


console = Console()


def show_success(message):
    """Display a success message."""
    console.print(f"[bold green]Success:[/bold green] {message}")


def show_error(message):
    """Display a readable error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def show_info(message):
    """Display an informational message."""
    console.print(message)


def show_users(users):
    """Display users in a formatted table."""
    if not users:
        console.print("No users found.")
        return

    table = Table(title="Users")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Email")
    table.add_column("Projects")

    for user in users:
        table.add_row(
            str(user.id),
            user.name,
            user.email,
            str(len(user.projects)),
        )

    console.print(table)


def show_projects(projects, manager):
    """Display projects in a formatted table."""
    if not projects:
        console.print("No projects found.")
        return

    table = Table(title="Projects")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Owner")
    table.add_column("Due Date")
    table.add_column("Tasks")

    for project in projects:
        owner = manager.find_project_owner(project.title)

        table.add_row(
            str(project.id),
            project.title,
            owner.name if owner else "Unknown",
            project.due_date or "None",
            str(len(project.tasks)),
        )

    console.print(table)


def show_tasks(tasks, project_title):
    """Display project tasks in a formatted table."""
    if not tasks:
        console.print(
            f"No tasks found for project '{project_title}'."
        )
        return

    table = Table(title=f"Tasks - {project_title}")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Assigned To")
    table.add_column("Contributors")

    for task in tasks:
        contributors = (
            ", ".join(task.contributors)
            if task.contributors
            else "None"
        )

        table.add_row(
            str(task.id),
            task.title,
            task.status,
            task.assigned_to or "Unassigned",
            contributors,
        )

    console.print(table)


def show_ai_summary(project_title, summary):
    """Display an AI-generated project summary."""
    console.print()
    console.rule(f"[bold]AI Summary: {project_title}")
    console.print(summary)
    console.rule()