import logging
from fastapi import APIRouter, HTTPException, Query
from src.recommendation_service.models.schemas import (
    RecommendationResponse, AnimeRecommendation,
    SimilarByIdResponse
)
from src.recommendation_service.services.content_based_service import HybridService
from src.recommendation_service.services.collaborative_service import CollaborativeService

logger = logging.getLogger(__name__)

router = APIRouter()
hybrid_service = HybridService()


def get_hybrid_service() -> HybridService:
    """Получить экземпляр гибридного сервиса"""
    return hybrid_service


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/recommend/text", response_model=RecommendationResponse)
async def recommend_by_text(
    q: str = Query(..., description="Search query", min_length=2),
    limit: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.3, ge=0, le=1)
):
    try:
        results, processing_time = await hybrid_service.recommend_by_text(q, limit, min_score)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

    return RecommendationResponse(
        query=q,
        results=[AnimeRecommendation(**r) for r in results],
        processing_time_ms=round(processing_time, 2)
    )


@router.get("/recommend/anime/{anime_id}", response_model=SimilarByIdResponse)
async def recommend_by_anime_id(
    anime_id: int,
    limit: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.5, ge=0, le=4),
    text_weight: float = Query(1.0, ge=0, le=2),
    genre_weight: float = Query(1.0, ge=0, le=2),
    theme_weight: float = Query(0.8, ge=0, le=2),
    demo_weight: float = Query(0.5, ge=0, le=2)
):
    try:
        results, processing_time = await hybrid_service.recommend_by_anime_id(
            anime_id, limit, min_score, text_weight, genre_weight, theme_weight, demo_weight
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

    return SimilarByIdResponse(
        anime_id=anime_id,
        recommendations=[AnimeRecommendation(**r) for r in results],
        processing_time_ms=round(processing_time, 2)
    )


@router.get("/weights")
async def get_weights():
    try:
        return await hybrid_service.get_weights()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/recommend/collaborative/{user_id}")
async def get_collaborative_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    return await CollaborativeService.get_recommendations(user_id, limit)


@router.get("/collaborative/status")
async def collaborative_status():
    return await CollaborativeService.get_status()