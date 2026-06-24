from sqlalchemy.orm import Session
from models.memo import Memo

class MemoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Memo).all()

    def get_by_id(self, memo_id: int):
        return self.db.query(Memo).filter(Memo.id == memo_id).first()

    def create(self, title: str, content: str):
        memo = Memo(title=title, content=content)
        self.db.add(memo)
        self.db.commit()
        return memo

    def update(self, memo_id: int, title: str, content: str):
        memo = self.get_by_id(memo_id)
        if memo:
            memo.title = title
            memo.content = content
            self.db.commit()
        return memo

    def delete(self, memo_id: int):
        memo = self.get_by_id(memo_id)
        if memo:
            self.db.delete(memo)
            self.db.commit()