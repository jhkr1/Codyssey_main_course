from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from services.memo_service import MemoService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/memos")
def list_memos(db: Session = Depends(get_db), request: Request = None):
    service = MemoService(db)
    return templates.TemplateResponse("list.html", {"request": request, "memos": service.get_memos()})

@router.post("/memos/create")
def create_memo(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    MemoService(db).create_memo(title, content)
    return RedirectResponse(url="/memos", status_code=303)