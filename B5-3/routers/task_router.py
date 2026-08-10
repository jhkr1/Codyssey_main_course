from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from services.project_service import ProjectService
from services.task_service import TaskService
from templates_config import templates


router = APIRouter()


@router.get("/projects/{project_id}/tasks/new")
def task_form(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        project = ProjectService(db).get_project(project_id, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Project not found.") from error

    return templates.TemplateResponse(
        request=request,
        name="tasks/form.html",
        context={"current_user": current_user, "project": project},
    )


@router.post("/projects/{project_id}/tasks")
def create_task(
    project_id: int,
    title: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        TaskService(db).create_task(project_id, current_user.id, title, description)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Project not found.") from error

    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.post("/tasks/{task_id}/status")
def change_task_status(
    task_id: int,
    target_status: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        task = TaskService(db).change_task_status(
            task_id,
            current_user.id,
            target_status,
        )
    except ValueError as error:
        status_code = 400 if str(error) == "Invalid task status transition." else 404
        raise HTTPException(status_code=status_code, detail=str(error)) from error

    return RedirectResponse(url=f"/projects/{task.project_id}", status_code=303)
