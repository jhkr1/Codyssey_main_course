from fastapi import Depends, Request
from sqlalchemy.orm import Session

from auth.exceptions import AuthenticationRequiredError
from database import get_db
from repositories.user_repo import UserRepository


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise AuthenticationRequiredError("Login is required.")

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise AuthenticationRequiredError("Session user does not exist.")

    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if user_id is None:
        return None

    return UserRepository(db).get_by_id(user_id)
