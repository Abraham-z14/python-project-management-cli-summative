from models import User, Project, Task


class ProjectManager:
    """Coordinate users, projects, tasks, persistence, and AI summaries."""

    def __init__(self, storage, ai_client=None):
        """Load saved users and store service dependencies."""
        self.storage = storage
        self.ai_client = ai_client
        self.users = self.storage.load_users()

    def save(self):
        """Persist the current application state."""
        self.storage.save_users(self.users)

    def find_user(self, name):
        """Return a user matching the supplied name."""
        if not isinstance(name, str) or not name.strip():
            return None

        clean_name = name.strip().lower()

        for user in self.users:
            if user.name.lower() == clean_name:
                return user

        return None

    def find_project(self, title):
        """Search all users for a project matching the supplied title."""
        if not isinstance(title, str) or not title.strip():
            return None

        clean_title = title.strip().lower()

        for user in self.users:
            for project in user.projects:
                if project.title.lower() == clean_title:
                    return project

        return None

    def find_project_owner(self, title):
        """Return the user who owns a project."""
        if not isinstance(title, str) or not title.strip():
            return None

        clean_title = title.strip().lower()

        for user in self.users:
            for project in user.projects:
                if project.title.lower() == clean_title:
                    return user

        return None

    def add_user(self, name, email):
        """Create and persist a new user."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("User name cannot be empty.")

        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email cannot be empty.")

        clean_name = name.strip()
        clean_email = email.strip()

        if self.find_user(clean_name):
            raise ValueError(f"User '{clean_name}' already exists.")

        for user in self.users:
            if user.email.lower() == clean_email.lower():
                raise ValueError(
                    f"Email '{clean_email}' is already in use."
                )

        user = User(clean_name, clean_email)
        self.users.append(user)
        self.save()

        return user

    def add_project(
        self,
        user_name,
        title,
        description="",
        due_date=None,
    ):
        """Create a project and attach it to an existing user."""
        user = self.find_user(user_name)

        if user is None:
            raise ValueError(f"User '{user_name}' not found.")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Project title cannot be empty.")

        clean_title = title.strip()

        if self.find_project(clean_title):
            raise ValueError(
                f"Project '{clean_title}' already exists."
            )

        project = Project(
            clean_title,
            description.strip() if description else "",
            due_date.strip() if due_date else None,
        )

        user.add_project(project)
        self.save()

        return project

    def update_project(
        self,
        project_title,
        new_title=None,
        description=None,
        due_date=None,
    ):
        """Update editable project fields and persist the changes."""
        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        if new_title is not None:
            clean_new_title = new_title.strip()

            if not clean_new_title:
                raise ValueError("Project title cannot be empty.")

            existing = self.find_project(clean_new_title)

            if existing is not None and existing is not project:
                raise ValueError(
                    f"Project '{clean_new_title}' already exists."
                )

            project.title = clean_new_title

        if description is not None:
            project.description = description

        if due_date is not None:
            project.due_date = due_date

        self.save()
        return project

    def add_task(
        self,
        project_title,
        task_title,
        assigned_to=None,
        contributors=None,
    ):
        """Create a task and attach it to an existing project."""
        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        if not isinstance(task_title, str) or not task_title.strip():
            raise ValueError("Task title cannot be empty.")

        clean_task_title = task_title.strip()

        for existing_task in project.tasks:
            if existing_task.title.lower() == clean_task_title.lower():
                raise ValueError(
                    f"Task '{clean_task_title}' already exists "
                    f"in project '{project.title}'."
                )

        clean_assignee = (
            assigned_to.strip()
            if isinstance(assigned_to, str) and assigned_to.strip()
            else None
        )

        task = Task(
            clean_task_title,
            assigned_to=clean_assignee,
        )

        for contributor in contributors or []:
            if isinstance(contributor, str) and contributor.strip():
                task.add_contributor(contributor.strip())

        project.add_task(task)
        self.save()

        return task

    def update_task(
        self,
        project_title,
        task_title,
        new_title=None,
        assigned_to=None,
        status=None,
    ):
        """Update editable task fields and persist the changes."""
        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        task = project.get_task(task_title)

        if task is None:
            raise ValueError(
                f"Task '{task_title}' not found "
                f"in project '{project.title}'."
            )

        if new_title is not None:
            clean_new_title = new_title.strip()

            if not clean_new_title:
                raise ValueError("Task title cannot be empty.")

            for existing_task in project.tasks:
                if (
                    existing_task is not task
                    and existing_task.title.lower()
                    == clean_new_title.lower()
                ):
                    raise ValueError(
                        f"Task '{clean_new_title}' already exists "
                        f"in project '{project.title}'."
                    )

            task.title = clean_new_title

        if assigned_to is not None:
            task.assigned_to = assigned_to

        if status is not None:
            task.status = status

        self.save()
        return task

    def add_contributor(
        self,
        project_title,
        task_title,
        contributor,
    ):
        """Add a contributor to a task and persist the relationship."""
        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        task = project.get_task(task_title)

        if task is None:
            raise ValueError(
                f"Task '{task_title}' not found "
                f"in project '{project.title}'."
            )

        task.add_contributor(contributor)
        self.save()

        return task

    def complete_task(self, project_title, task_title):
        """Mark a project task as complete and persist the change."""
        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        completed_task = project.complete_task(task_title)
        self.save()

        return completed_task

    def list_users(self):
        """Return a copy of all users."""
        return list(self.users)

    def list_projects(self, user_name=None):
        """Return projects for one user or every project."""
        if user_name:
            user = self.find_user(user_name)

            if user is None:
                raise ValueError(
                    f"User '{user_name}' not found."
                )

            return list(user.projects)

        projects = []

        for user in self.users:
            projects.extend(user.projects)

        return projects

    def list_tasks(self, project_title):
        """Return all tasks belonging to one project."""
        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        return list(project.tasks)

    def summarize_project(self, project_title):
        """Generate an AI summary from structured project/task data."""
        if self.ai_client is None:
            raise RuntimeError("No AI client is configured.")

        project = self.find_project(project_title)

        if project is None:
            raise ValueError(
                f"Project '{project_title}' not found."
            )

        task_lines = []

        for task in project.tasks:
            contributor_text = (
                ", ".join(task.contributors)
                if task.contributors
                else "None"
            )

            task_lines.append(
                f"- {task.title}\n"
                f"  Status: {task.status}\n"
                f"  Assigned to: "
                f"{task.assigned_to or 'Unassigned'}\n"
                f"  Contributors: {contributor_text}"
            )

        tasks_text = (
            "\n".join(task_lines)
            if task_lines
            else "No tasks."
        )

        prompt = f"""
Create a concise project-management summary using only the information below.

Project: {project.title}
Description: {project.description or "No description provided"}
Due date: {project.due_date or "No due date provided"}

Tasks:
{tasks_text}

Include:
1. Current project status
2. Completed work
3. Remaining work
4. Potential risks
5. Suggested next step

Do not invent facts that are not present in the project data.
""".strip()

        return self.ai_client.send(prompt)