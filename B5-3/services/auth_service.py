from repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)

    def authenticate(self, username: str, password: str):
        user = self.user_repo.get_by_username(username)
        if not user or user.password != password:
            return None
        return user
