from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="projects")

    # Task는 Project에 종속되어 독립적인 비즈니스 의미가 없으므로,
    # Project 삭제 시 소속 Task도 함께 삭제한다.
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )
