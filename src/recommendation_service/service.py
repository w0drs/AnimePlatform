from src.recommendation_service.recommender import LanceRecommender
from src.recommendation_service.schemas import RecommendationResponse, AnimeRecommendation, SimilarByIdResponse
import time
from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager


# Глобальные переменные
recommender: LanceRecommender | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global recommender

    # Загрузка при старте
    print("Загрузка рекомендера...")
    recommender = LanceRecommender(db_path="src/recommendation_service/lancedb")

    try:
        recommender.table = recommender.db.open_table(recommender.table_name)
        print(f"LanceDB загружен: {recommender.table_name}")
    except Exception as e:
        print(f"Таблица не найдена: {e}")
        print("Запустите 'python sync.py' для синхронизации")

    yield

    print("Выключение сервиса...")


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
    """Проверка работоспособности"""
    return {"status": "ok"}


@app.get("/recommend/text", response_model=RecommendationResponse)
async def recommend_by_text(
        q: str = Query(..., description="Поисковый запрос", min_length=2),
        limit: int = Query(10, description="Количество результатов", ge=1, le=50),
        min_score: float = Query(0.3, description="Минимальная схожесть", ge=0, le=1)
):
    """Поиск похожих аниме по текстовому запросу"""
    start_time = time.time()

    try:
        results = recommender.find_similar(q, limit=limit, min_score=min_score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")

    processing_time = (time.time() - start_time) * 1000

    return RecommendationResponse(
        query=q,
        results=[AnimeRecommendation(**r) for r in results],
        processing_time_ms=round(processing_time, 2)
    )


@app.get("/recommend/anime/{anime_id}", response_model=SimilarByIdResponse)
async def recommend_by_anime_id(
        anime_id: int,
        limit: int = Query(10, description="Количество результатов", ge=1, le=50)
):
    """Поиск похожих аниме по ID аниме"""
    start_time = time.time()
    try:
        results = recommender.recommend_by_id(anime_id, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")

    processing_time = (time.time() - start_time) * 1000
    return SimilarByIdResponse(
        anime_id=anime_id,
        recommendations=[AnimeRecommendation(**r) for r in results],
        processing_time_ms=round(processing_time, 2)
    )
