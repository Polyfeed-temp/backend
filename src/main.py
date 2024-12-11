from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from src.user import router as user_router
from src.unit import router as unit_router
from src.login import router as login_router
from src.openai import router as openai_router
from src.feedback import router as feedback_router
from src.highlight import router as highlight_router
from src.action import router as action_router
from src.log import router as log_router
from src.file import router as file_router


from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

config = Config('.env')



app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=config('RANDOM_SECRET_KEY', cast=str))

app.add_middleware(CORSMiddleware,  allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH"],
    allow_headers=["Content-Type","Set-Cookie", "Authorization"])

app.body_limit = 100 * 1024 * 1024  # 100MB in bytes



# app.include_router(annotation_router.router, prefix="/api/annotation", tags=["annotation"], dependencies=[Depends(oauth2_scheme)])
app.include_router(user_router.router, prefix="/api/user", tags=["user"])
app.include_router(unit_router.router, prefix="/api/unit", tags=["unit"])
# app.include_router(assessment_router.router, prefix="/api/assessment", tags=["assessment"])
# app.include_router(enrollment_router.router, prefix="/api/enrollment", tags=["enrollment"])
app.include_router(feedback_router.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(highlight_router.router, prefix="/api/highlight", tags=["highlight"])
app.include_router(action_router.router, prefix="/api/action", tags=["action"])
app.include_router(login_router.router, prefix="/api/login", tags=["login"])
app.include_router(openai_router.router, prefix="/api/openai", tags=["openai"])
app.include_router(file_router.router, prefix="/api/file", tags=["file"])
# logs route
app.include_router(log_router.router, prefix="/api/logs", tags=["logs"])


@app.get("/healthcheck",tags=["health check"])
def healthcheck():
    return {"status": "ok"}
@app.get('/signup', response_class=HTMLResponse)
def signup(request: Request):
    return templates.TemplateResponse('signup.html', {'request': request})
@app.get('/', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/guide', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('guide.html', {'request': request})


@app.get('/privacypolicy', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('privacypolicy.html', {'request': request})


@app.get('/about-learner-centered-feedback', response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse('learner-centered-feedback.html', {'request': request})