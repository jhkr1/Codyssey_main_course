from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from services.memo_service import MemoService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

@router.get("/memos")
def list_memos(db: Session = Depends(get_db), request: Request = None):
    service = MemoService(db)
    return templates.TemplateResponse(request=request, name="list.html", context={"request": request, "memos": service.get_memos()})

@router.get("/memos/create")
def create_memo_form(request: Request):
    return templates.TemplateResponse(request=request, name="form.html", context={"request": request, "memo": None})

@router.post("/memos/create")
def create_memo(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    MemoService(db).create_memo(title, content)
    return RedirectResponse(url="/memos", status_code=303)

@router.get("/memos/{memo_id}")
def get_memo_detail(memo_id: int, request: Request, db: Session = Depends(get_db)):
    memo = MemoService(db).get_memo(memo_id)
    if not memo:
        # 요구사항: 존재하지 않는 데이터 조회 시 예외처리
        raise HTTPException(status_code=404, detail="해당 메모를 찾을 수 없습니다.")
    return templates.TemplateResponse(request=request, name="detail.html", context={"request": request, "memo": memo})

@router.get("/memos/{memo_id}/edit")
def edit_memo_form(memo_id: int, request: Request, db: Session = Depends(get_db)):
    memo = MemoService(db).get_memo(memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="해당 메모를 찾을 수 없습니다.")
    return templates.TemplateResponse(request=request, name="form.html", context={"request": request, "memo": memo})

@router.post("/memos/{memo_id}/edit")
def update_memo(memo_id: int, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    memo = MemoService(db).update_memo(memo_id, title, content)
    if not memo:
        raise HTTPException(status_code=404, detail="해당 메모를 찾을 수 없습니다.")
    return RedirectResponse(url=f"/memos/{memo_id}", status_code=303)

@router.post("/memos/{memo_id}/delete")
def delete_memo(memo_id: int, db: Session = Depends(get_db)):
    MemoService(db).delete_memo(memo_id)
    return RedirectResponse(url="/memos", status_code=303)