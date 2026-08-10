from repositories.project_repo import ProjectRepository
from repositories.task_repo import TaskRepository


class TaskService:
    def __init__(self, db):
        self.project_repo = ProjectRepository(db)
        self.task_repo = TaskRepository(db)

    def get_tasks(self, project_id: int, user_id: int):
        self._get_owned_project(project_id, user_id)
        return self.task_repo.get_by_project_id(project_id)

    def create_task(
        self,
        project_id: int,
        user_id: int,
        title: str,
        description: str,
    ):
        self._get_owned_project(project_id, user_id)
        return self.task_repo.create(
            title=title,
            description=description,
            status="TODO",
            project_id=project_id,
        )

    def get_task(self, task_id: int, user_id: int):
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found or access denied.")

        self._get_owned_project(task.project_id, user_id)
        return task

    def change_task_status(self, task_id: int, user_id: int, target_status: str):
        task = self.get_task(task_id, user_id)
        allowed_transitions = {
            "TODO": "IN_PROGRESS",
            "IN_PROGRESS": "DONE",
        }

        if allowed_transitions.get(task.status) != target_status:
            raise ValueError("Invalid task status transition.")

        task.status = target_status
        return self.task_repo.save(task)

    def _get_owned_project(self, project_id: int, user_id: int):
        project = self.project_repo.get_by_id_and_user_id(project_id, user_id)
        if not project:
            raise ValueError("Project not found or access denied.")
        return project
