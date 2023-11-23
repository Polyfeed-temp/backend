# authorization.py
import json
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2AuthorizationCodeBearer
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import HTMLResponse
import os

router = APIRouter()

config = Config('.env')
oauth = OAuth(config)
oauth.register(
    "app",
    client_id=config('GOOGLE_CLIENT_ID', cast=str),
    client_secret=config('GOOGLE_CLIENT_SECRET', cast=str),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=config('META_URL', cast=str),
)

templates = Jinja2Templates(directory="C:/Users/tonyz/Desktop")


@router.get("/")
async def home(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("home.html",
                                      {"request": request, "user": user, "pretty": json.dumps(user, indent=4)})


@router.get("/signin-google")
async def googleCallback(request: Request):
    token = await oauth.app.authorize_access_token(request)
    request.session["user"] = dict(token)
    print("session: ", request.session.get("user"))
    # return RedirectResponse(url="http://127.0.0.1:5500/home.html")
    return RedirectResponse(url="http://localhost:3000/")


@router.get("/google-login")
async def googleLogin(request: Request):
    user = request.session.get("user")
    # if user:
    #     raise HTTPException(status_code=404, detail="User already logged in")
    redirect_uri = request.url_for("googleCallback")
    return await oauth.app.authorize_redirect(request, redirect_uri)


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    # return RedirectResponse(url="http://127.0.0.1:5500/home.html")
    return RedirectResponse(url="http://localhost:3000/")


@router.get("/get-user")
async def get_user(request: Request):
    user = request.session.get("user")
    print(f"User data in session: {user}")  # add this line
    return {"user": user}
