from fastapi import FastAPI, Depends
from src.annotation import router as annotation_router
from src.user import router as user_router


app = FastAPI()

app.include_router(annotation_router.router, prefix="/api/annotation", tags=["annotation"])
app.include_router(user_router.router, prefix="/api/user", tags=["user"])
