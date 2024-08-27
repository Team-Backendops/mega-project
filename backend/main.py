from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from routers import service
from core.database import init_db

app = FastAPI()

app.include_router(user.router)
app.include_router(service.router)
# app.include_router(review.router)

frontend_directory = os.path.join(os.path.dirname(__file__), "..", "frontend")

if not os.path.isdir(frontend_directory):
    raise RuntimeError(f"Directory '{frontend_directory}' does not exist")

app.mount("/static", StaticFiles(directory=frontend_directory), name="static")


@app.get("/{file_name}")
async def get_file(file_name: str):
    if file_name in ["index.html", "login.html", "register.html"]:
        file_path = os.path.join(frontend_directory, file_name)
        if os.path.isfile(file_path):
            return StaticFiles(directory=frontend_directory).app(scope={"type": "http", "path": f"/static/{file_name}"},
                                                                 receive=None)
        raise HTTPException(status_code=404, detail="File not found")
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
