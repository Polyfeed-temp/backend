from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.annotation import router as annotation_router
from src.user import router as user_router
from src.unit import router as unit_router
from src.assessment import router as assessment_router


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(annotation_router.router, prefix="/api/annotation", tags=["annotation"])
app.include_router(user_router.router, prefix="/api/user", tags=["user"])
app.include_router(unit_router, prefix="/api/unit", tags=["unit"])
app.include_router(assessment_router, prefix="/api/assessment", tags=["assessment"])
