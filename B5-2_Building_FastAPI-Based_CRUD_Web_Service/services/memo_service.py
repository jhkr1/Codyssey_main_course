from repositories.memo_repo import MemoRepository

class MemoService:
    def __init__(self, db):
        self.repo = MemoRepository(db)

    def get_memos(self):
        return self.repo.get_all()

    def get_memo(self, memo_id):
        return self.repo.get_by_id(memo_id)

    def create_memo(self, title, content):
        return self.repo.create(title, content)

    def update_memo(self, memo_id, title, content):
        return self.repo.update(memo_id, title, content)

    def delete_memo(self, memo_id):
        return self.repo.delete(memo_id)