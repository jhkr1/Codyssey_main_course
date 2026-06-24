from sqlalchemy import Column, Integer, String
from database import Base

class Memo(Base):
    __tablename__ = "memos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)