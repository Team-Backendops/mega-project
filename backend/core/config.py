import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
    app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY', 'secretKey'), max_age=1800)  # 30 minutes
    return app
