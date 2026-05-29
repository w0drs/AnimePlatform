from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from src.anime_service.api.routes import anime, search, news
from src.anime_service.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом"""
    print("Starting Anime API...")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Anime API",
    description="CRUD API для аниме",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(anime.router)
app.include_router(search.router)
app.include_router(news.router)

@app.get("/")
async def root():
    return {"message": "Anime API", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "crud_service:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )