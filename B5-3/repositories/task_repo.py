from sqlalchemy.orm import Session

from models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int):
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_by_project_id(self, project_id: int):
        return self.db.query(Task).filter(Task.project_id == project_id).all()

    def create(
        self,
        title: str,
        description: str,
        status: str,
        project_id: int,
    ):
        task = Task(
            title=title,
            description=description,
            status=status,
            project_id=project_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def save(self, task: Task):
        self.db.commit()
        self.db.refresh(task)
        return task
