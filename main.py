import os
import pydantic
from typing import Union
from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()
app = FastAPI()
app.mount("/static/Photo", StaticFiles(directory="static/Photo"), name="Photo")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.mount("/static", StaticFiles(directory = "static"), name = "static")
templates = Jinja2Templates(directory = "templates")

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile https://www.googleapis.com/auth/contacts.readonly"},
)

@app.get("/", response_class = HTMLResponse)
async def read_root(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("index.html", {"request":request, "user": user})

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)

#profile
@app.get("/profile")
async def profile(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url = "/")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

#Contacts
@app.get("/contacts", response_class=HTMLResponse)
async def contacts(request: Request):
    token = request.session.get("token")
    if not token:
        return RedirectResponse(url = "/login")
    resp = await oauth.google.get(
        "https://people.googleapis.com/v1/people/me/connections",
        params = {"personFields": "names,emailAddresses"},
        token = token,
    )
    
    data = resp.json()
    contacts = []
    for person in data.get("connections", []):
        name = person.get("names", [{}])[0].get("displayName", "Unknown")
        email = person.get("emailAddresses", [{}])[0].get("value", "No Email")
        contacts.append({"name": name, "email": email})
    return templates.TemplateResponse("contacts.html", {"request": request, "contacts": contacts})

#After google Login
@app.get("/auth/callback")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")
    request.session["user"] = user
    request.session["token"] = token    
    return RedirectResponse(url = "/")
    

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url = "/")

