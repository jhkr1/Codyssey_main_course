from fastapi import FastAPI
from database import engine, Base
from routers import memo_router

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="나의 메모 앱")

# 라우터 등록
app.include_router(memo_router.router)
