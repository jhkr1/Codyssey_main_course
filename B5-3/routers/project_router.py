from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from services.project_service import ProjectService
from services.task_service import TaskService
from templates_config import templates


router = APIRouter(prefix="/projects")


@router.get("")
def list_projects(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    projects = ProjectService(db).get_projects(current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="projects/list.html",
        context={"current_user": current_user, "projects": projects},
    )


@router.get("/new")
def project_form(
    request: Request,
    current_user=Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="projects/form.html",
        context={"current_user": current_user},
    )


@router.post("")
def create_project(
    title: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ProjectService(db).create_project(title, description, current_user.id)
    return RedirectResponse(url="/projects", status_code=303)


@router.get("/{project_id}")
def project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        project = ProjectService(db).get_project(project_id, current_user.id)
        tasks = TaskService(db).get_tasks(project_id, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Project not found.") from error

    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={"current_user": current_user, "project": project, "tasks": tasks},
    )


@router.post("/{project_id}/delete")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        ProjectService(db).delete_project(project_id, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Project not found.") from error

    return RedirectResponse(url="/projects", status_code=303)
