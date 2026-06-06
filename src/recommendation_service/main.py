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
from src.recommendation_service.recommenders.hybrid import HybridRecommender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные переменные
hybrid_recommender: HybridRecommender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global hybrid_recommender

    logger.info("Загрузка гибридного рекомендера...")
    hybrid_recommender = HybridRecommender()

    try:
        hybrid_recommender.table = hybrid_recommender.db.open_table(hybrid_recommender.table_name)
        logger.info(f"LanceDB загружен: {hybrid_recommender.table_name}")

        # Настройка весов (можно менять)
        hybrid_recommender.update_weights(
            text_weight=1.0,
            genre_weight=1.0,
            theme_weight=0.8,
            demographic_weight=0.5
        )
    except Exception as e:
        logger.warning(f"Таблица не найдена: {e}")

    yield

    logger.info("Выключение сервиса...")


app = FastAPI(
    title="Anime Recommendation API",
    description="Гибридные рекомендации аниме (текст + жанры + темы + демографика)",
    version="2.0.0",
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

    if hybrid_recommender is None or hybrid_recommender.table is None:
        raise HTTPException(status_code=503, detail="Recommender not loaded")

    try:
        results = hybrid_recommender.find_similar_by_text(q, limit=limit, min_score=min_score)
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
        limit: int = Query(10, ge=1, le=50),
        min_score: float = Query(0.5, ge=0, le=4),
        text_weight: float = Query(1.0, ge=0, le=2),
        genre_weight: float = Query(1.0, ge=0, le=2),
        theme_weight: float = Query(0.8, ge=0, le=2),
        demo_weight: float = Query(0.5, ge=0, le=2)
):
    """
    Гибридные рекомендации на основе:
    - Похожести описаний
    - Совпадения жанров
    - Совпадения тем
    - Совпадения демографики

    Также учитывается возрастной рейтинг (не рекомендуются более высокие рейтинги)
    """
    start_time = time.time()

    if hybrid_recommender is None or hybrid_recommender.table is None:
        raise HTTPException(status_code=503, detail="Recommender not loaded")

    # Обновляем веса для этого запроса
    hybrid_recommender.update_weights(
        text_weight=text_weight,
        genre_weight=genre_weight,
        theme_weight=theme_weight,
        demographic_weight=demo_weight
    )

    try:
        results = hybrid_recommender.find_similar_by_id(anime_id, limit=limit, min_score=min_score)
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


@app.get("/weights")
async def get_weights():
    """Получить текущие веса компонентов"""
    if hybrid_recommender is None:
        raise HTTPException(status_code=503, detail="Recommender not loaded")

    return hybrid_recommender.weights


@app.get("/recommend/collaborative/{user_id}")
async def get_collaborative_recommendations(
        user_id: str,
        limit: int = Query(10, ge=1, le=50)
):
    """Получить коллаборативные рекомендации из БД (сгенерированные офлайн)"""
    try:
        conn = psycopg2.connect(**settings.pg_params)
        cur = conn.cursor()

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