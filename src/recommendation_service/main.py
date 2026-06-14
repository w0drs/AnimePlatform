import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.recommendation_service.api.routes import router, hybrid_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    hybrid_service.init_recommender()
    yield
    logger.info("Выключение сервиса...")


app = FastAPI(
    title="Anime Recommendation API",
    description="Гибридные рекомендации аниме (текст + жанры + темы + демографика)",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Anime Recommendation API", "status": "running"}