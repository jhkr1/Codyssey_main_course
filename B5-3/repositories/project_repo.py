from sqlalchemy.orm import Session

from models.project import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int):
        return self.db.query(Project).filter(Project.user_id == user_id).all()

    def get_by_id(self, project_id: int):
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_by_id_and_user_id(self, project_id: int, user_id: int):
        return (
            self.db.query(Project)
            .filter(Project.id == project_id, Project.user_id == user_id)
            .first()
        )

    def create(self, title: str, description: str, user_id: int):
        project = Project(title=title, description=description, user_id=user_id)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int):
        project = self.get_by_id(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
