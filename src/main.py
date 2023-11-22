from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.annotation import router as annotation_router
from src.user import router as user_router


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(annotation_router.router, prefix="/api/annotation", tags=["annotation"])
app.include_router(user_router.router, prefix="/api/user", tags=["user"])
