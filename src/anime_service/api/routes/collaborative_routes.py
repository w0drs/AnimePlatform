from fastapi import APIRouter, HTTPException, Depends, Query
from uuid import UUID
from typing import Optional
from src.anime_service.database.connection import db
from src.anime_service.api.deps import get_current_user

router = APIRouter(prefix="/collaborative", tags=["collaborative"])


@router.get("/recommendations")
async def get_recommendations(
        user: dict = Depends(get_current_user),
        limit: int = Query(20, ge=1, le=100),
        model_version: Optional[int] = Query(None, description="Версия модели")
):
    """
    Получить готовые рекомендации из БД
    """
    #user_id = UUID(user.get("user_id"))

    return {
        "user_id": "loh", # str(user_id),
        "recommendations": [
            {
            #    "anime_id": r['anime_id'],
            #    "title": r['title_english'],
            #    "image_url": r['image_webp_large_url'],
            #    "score": r['score'],
            #    "rank": r['rank']
            }
            # for r in results
        ],
        #"total": len(results),
        "model_version": model_version
    }


@router.get("/interactions/my")
async def get_my_interactions(
        user: dict = Depends(get_current_user),
        limit: int = Query(100, le=1000)
):
    """
    Получить историю взаимодействий пользователя
    """
    #user_id = UUID(user.get("user_id"))

    return {
        #"user_id": str(user_id),
        #"interactions": results,
        #"total": len(results)
    }
