from repositories.project_repo import ProjectRepository


class ProjectService:
    def __init__(self, db):
        self.repo = ProjectRepository(db)

    def get_projects(self, user_id: int):
        return self.repo.get_by_user_id(user_id)

    def get_project(self, project_id: int, user_id: int):
        project = self.repo.get_by_id_and_user_id(project_id, user_id)
        if not project:
            raise ValueError("Project not found or access denied.")
        return project

    def create_project(self, title: str, description: str, user_id: int):
        return self.repo.create(title, description, user_id)

    def delete_project(self, project_id: int, user_id: int):
        project = self.get_project(project_id, user_id)
        self.repo.delete(project.id)
