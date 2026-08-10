from database import SessionLocal
from repositories.user_repo import UserRepository


TEST_USERNAME = "test"
TEST_PASSWORD = "1234"


def ensure_test_user():
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        if not user_repo.get_by_username(TEST_USERNAME):
            user_repo.create(TEST_USERNAME, TEST_PASSWORD)
    finally:
        db.close()
