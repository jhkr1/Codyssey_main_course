from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from auth.bootstrap import ensure_test_user
from auth.config import SESSION_SECRET_KEY
from auth.exceptions import AuthenticationRequiredError
from database import Base, engine
import models  # 모든 ORM 모델을 import하여 metadata에 등록한다.
from routers import auth_router, project_router, task_router


Base.metadata.create_all(bind=engine)
ensure_test_user()

app = FastAPI(title="Project Task Manager")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, same_site="lax")


@app.exception_handler(AuthenticationRequiredError)
def redirect_to_login(request: Request, exc: AuthenticationRequiredError):
    return RedirectResponse(url="/login", status_code=303)


app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(task_router.router)
