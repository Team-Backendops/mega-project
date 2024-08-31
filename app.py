from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY', 'secretKey'), max_age=1800)  # 30 minute

templates = Jinja2Templates(directory="templates")
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["mydatabase"]
users = db["users"]

class UserModel(BaseModel):
    username: str
    password: str

class RegisterModel(BaseModel):
    username: str
    password: str
    confirm_password: str

@app.get("/login")
async def login(request: Request, message: str = None):
    message = request.query_params.get("message", "")
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.post("/login")
async def post_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    # Fetch the user from the database
    user = users.find_one({"username": username})
    if not user:
        return RedirectResponse(url="/login?message=User does not exist", status_code=status.HTTP_302_FOUND)

    # Ensure the password from the database is in bytes before comparison
    stored_hashed_password = user['password']
    if isinstance(stored_hashed_password, str):
        stored_hashed_password = stored_hashed_password.encode('utf-8')

    if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        return RedirectResponse(url="/login?message=Invalid password", status_code=status.HTTP_302_FOUND)

    # Login successful
    request.session['user'] = username
    return RedirectResponse(url="/protected?message=Login successful", status_code=status.HTTP_302_FOUND)


@app.get("/protected")
async def protected(request: Request, message: str = None):
    if 'user' not in request.session:
        message = request.query_params.get("message", "")
        return RedirectResponse(url="/login?message=Session expired. Please log in again.", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("protected.html", {"request": request, "user": request.session['user'], "message": message})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login?message=You have been logged out.", status_code=status.HTTP_302_FOUND)

@app.get("/register")
async def register(request: Request, message: str = None):
    message = request.query_params.get("message", "")
    return templates.TemplateResponse("register.html", {"request": request, "message": message})

@app.post("/register")
async def post_register(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    confirm_password = form.get("confirm_password")

    if password != confirm_password:
        return RedirectResponse(url="/register?message=Passwords do not match", status_code=status.HTTP_302_FOUND)

    if not username or not password or not confirm_password:
        return RedirectResponse(url="/register?message=Please fill in all fields", status_code=status.HTTP_302_FOUND)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({"username": username, "password": hashed_password})

    return RedirectResponse(url="/login?message=Registration successful. Please log in.", status_code=status.HTTP_302_FOUND)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)