import logging
from typing import Dict, Any
from src.recommendation_service.repositories.collaborative_repo import CollaborativeRepository

logger = logging.getLogger(__name__)


class CollaborativeService:
    """Сервис для работы с коллаборативными рекомендациями"""

    @staticmethod
    async def get_recommendations(user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Получить рекомендации для пользователя"""
        try:
            results = CollaborativeRepository.get_recommendations(user_id, limit)

            return {
                "user_id": user_id,
                "recommendations": [
                    {"id": row[0], "title_english": row[1]} for row in results
                ],
                "total": len(results)
            }
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {e}")
            raise

    @staticmethod
    async def get_status() -> Dict[str, Any]:
        """Получить статус системы рекомендаций"""
        try:
            users_count, last_update = CollaborativeRepository.get_status()

            if not users_count or users_count == 0:
                return {"status": "no_data", "users_count": 0, "last_update": None}

            return {"status": "ready", "users_count": users_count, "last_update": last_update}
        except Exception as e:
            logger.error(f"Error getting collaborative status: {e}")
            return {"status": "error", "message": str(e)}