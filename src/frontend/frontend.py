from src.frontend.routes import auth
from src.frontend.routes import anime
from src.frontend.routes import news
from src.frontend.routes import users
from src.frontend.routes import admins

from src.frontend.config.settings import settings

from pathlib import Path

import uvicorn
from starlette.staticfiles import StaticFiles
from fastapi import FastAPI

app = FastAPI(title="FastAPI Frontend")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(auth.router)
app.include_router(anime.router)
app.include_router(news.router)
app.include_router(admins.router)
app.include_router(users.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "frontend:app",
        host=settings.frontend_host,
        port=settings.frontend_port,
    )