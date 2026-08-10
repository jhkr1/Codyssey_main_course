from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_optional_current_user
from database import get_db
from services.auth_service import AuthService
from templates_config import templates


router = APIRouter()


@router.get("/")
def home(
    request: Request,
    current_user=Depends(get_optional_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"current_user": current_user},
    )


@router.get("/login")
def login_form(
    request: Request,
    current_user=Depends(get_optional_current_user),
):
    if current_user:
        return RedirectResponse(url="/projects", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"current_user": None, "error_message": None},
    )


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = AuthService(db).authenticate(username, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "current_user": None,
                "error_message": "아이디 또는 비밀번호가 올바르지 않습니다.",
            },
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/projects", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
