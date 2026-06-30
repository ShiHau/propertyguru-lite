from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from frontend.config import settings
from frontend.routes import router

PROJECT_ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(
    title=settings.frontend_app_name,
    description="PropertyGuru Lite frontend server",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(PROJECT_ROOT / "frontend" / "static")),
    name="static",
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("frontend.main:app", host="0.0.0.0", port=8080, reload=True)
