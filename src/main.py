from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.annotation import router as annotation_router
from src.user import router as user_router
from src.unit import router as unit_router
from src.assessment import router as assessment_router
from src.student_unit import router as student_unit_router
from src.login import router as login_router
from src.openai import router as openai_router
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from fastapi.security import OAuth2PasswordBearer

config = Config('.env')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/token")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config('RANDOM_SECRET_KEY', cast=str))

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
app.include_router(annotation_router.router, prefix="/api/annotation", tags=["annotation"], dependencies=[Depends(oauth2_scheme)])
app.include_router(user_router.router, prefix="/api/user", tags=["user"])
app.include_router(unit_router.router, prefix="/api/unit", tags=["unit"])
app.include_router(assessment_router.router, prefix="/api/assessment", tags=["assessment"])
app.include_router(student_unit_router.router, prefix="/api/student_unit", tags=["student_unit"])
app.include_router(login_router.router, prefix="/api/login", tags=["login"])
app.include_router(openai_router.router, prefix="/api/openai", tags=["openai"])
