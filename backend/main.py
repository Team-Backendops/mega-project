from fastapi import FastAPI
from core.config import create_app
from routers import user

app = create_app()

app.include_router(user.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
