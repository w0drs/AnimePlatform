import psycopg2
from typing import List, Tuple, Optional
from src.recommendation_service.config.settings import settings


class CollaborativeRepository:
    """Репозиторий для работы с коллаборативными рекомендациями в БД"""

    @staticmethod
    def get_recommendations(user_id: str, limit: int = 10) -> List[Tuple[int, str]]:
        """Получить рекомендации для пользователя"""
        with psycopg2.connect(**settings.pg_params) as conn:
            with conn.cursor() as cur:
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
                return cur.fetchall()

    @staticmethod
    def get_status() -> Tuple[int, Optional[str]]:
        """Получить статус рекомендаций (количество пользователей и дата последнего обновления)"""
        with psycopg2.connect(**settings.pg_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT user_id) as users_count,
                        MAX(created_at) as last_update
                    FROM collaborative_recommendations
                """)
                row = cur.fetchone()
                return row[0] if row else 0, row[1] if row else None