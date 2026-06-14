from src.frontend.routes import auth
from src.frontend.routes import anime
from src.frontend.routes import news
from src.frontend.routes import users
from src.frontend.routes import admins
from src.frontend.routes import comments
from src.frontend.routes import favorites
from src.frontend.config.settings import settings

from pathlib import Path

import uvicorn
from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="FastAPI Frontend")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(auth.router)
app.include_router(anime.router)
app.include_router(news.router)
app.include_router(admins.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(favorites.router)

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/landing", response_class=HTMLResponse)
def profile():
    return RedirectResponse(url="https://w0drs.github.io/AnimePlatform/", status_code=302)

if __name__ == "__main__":
    uvicorn.run(
        "frontend:app",
        host=settings.frontend_host,
        port=settings.frontend_port,
    )