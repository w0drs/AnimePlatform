import time
import logging
import psycopg2
from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager

from src.recommendation_service.config.settings import settings
from src.recommendation_service.models.schemas import (
    RecommendationResponse, AnimeRecommendation,
    SimilarByIdResponse
)
from src.recommendation_service.recommenders.content_based import LanceRecommender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные переменные
content_recommender: LanceRecommender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global content_recommender

    logger.info("Загрузка content-based рекомендера...")
    content_recommender = LanceRecommender()

    try:
        content_recommender.table = content_recommender.db.open_table(content_recommender.table_name)
        logger.info(f"LanceDB загружен: {content_recommender.table_name}")
    except Exception as e:
        logger.warning(f"Таблица не найдена: {e}")

    yield

    logger.info("Выключение сервиса...")


app = FastAPI(
    title="Anime Recommendation API",
    description="Content-based рекомендации аниме на LanceDB",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Anime Recommendation API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/recommend/text", response_model=RecommendationResponse)
async def recommend_by_text(
        q: str = Query(..., description="Search query", min_length=2),
        limit: int = Query(10, ge=1, le=50),
        min_score: float = Query(0.3, ge=0, le=1)
):
    start_time = time.time()

    if content_recommender is None or content_recommender.table is None:
        raise HTTPException(status_code=503, detail="Content recommender not loaded")

    try:
        results = content_recommender.find_similar(q, limit=limit, min_score=min_score)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

    processing_time = (time.time() - start_time) * 1000

    return RecommendationResponse(
        query=q,
        results=[AnimeRecommendation(**r) for r in results],
        processing_time_ms=round(processing_time, 2)
    )


@app.get("/recommend/anime/{anime_id}", response_model=SimilarByIdResponse)
async def recommend_by_anime_id(
        anime_id: int,
        limit: int = Query(10, ge=1, le=50)
):
    start_time = time.time()

    if content_recommender is None or content_recommender.table is None:
        raise HTTPException(status_code=503, detail="Content recommender not loaded")

    try:
        results = content_recommender.recommend_by_id(anime_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

    processing_time = (time.time() - start_time) * 1000

    return SimilarByIdResponse(
        anime_id=anime_id,
        recommendations=[AnimeRecommendation(**r) for r in results],
        processing_time_ms=round(processing_time, 2)
    )


@app.get("/recommend/collaborative/{user_id}")
async def get_collaborative_recommendations(
        user_id: str,
        limit: int = Query(10, ge=1, le=50)
):
    """Получить коллаборативные рекомендации из БД"""

    try:
        conn = psycopg2.connect(**settings.pg_params)
        cur = conn.cursor()

        # Получаем последние рекомендации для пользователя
        cur.execute("""
            SELECT cr.anime_id, a.title_english
            FROM collaborative_recommendations cr
            JOIN anime a ON cr.anime_id = a.id
            WHERE cr.user_id = %s
            AND cr.created_at = (
                SELECT MAX(created_at) 
                FROM collaborative_recommendations 
                WHERE user_id = %s
            )
            LIMIT %s
        """, (user_id, user_id, limit))

        results = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "user_id": user_id,
            "recommendations": [
                {
                    "id": row[0],
                    "title_english": row[1]
                }
                for row in results
            ],
            "total": len(results)
        }

    except Exception as e:
        logger.error(f"Error getting collaborative recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/collaborative/status")
async def collaborative_status():
    """Проверка наличия рекомендаций в БД"""
    try:
        conn = psycopg2.connect(**settings.pg_params)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                COUNT(DISTINCT user_id) as users_count,
                MAX(created_at) as last_update
            FROM collaborative_recommendations
        """)

        row = cur.fetchone()
        cur.close()
        conn.close()

        # Проверяем, что есть данные
        if not row or row[0] is None or row[0] == 0:
            return {
                "status": "no_data",
                "users_count": 0,
                "last_update": None
            }

        return {
            "status": "ready",
            "users_count": row[0],
            "last_update": row[1]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}