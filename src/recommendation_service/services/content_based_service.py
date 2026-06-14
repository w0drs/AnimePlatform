import time
import logging
from typing import List, Dict
from src.recommendation_service.recommenders.hybrid import HybridRecommender

logger = logging.getLogger(__name__)


class HybridService:
    """Сервис для гибридных рекомендаций"""

    def __init__(self):
        self.recommender: HybridRecommender | None = None

    def init_recommender(self) -> None:
        """Инициализация рекомендера"""
        logger.info("Загрузка гибридного рекомендера...")
        self.recommender = HybridRecommender()

        try:
            self.recommender.table = self.recommender.db.open_table(self.recommender.table_name)
            logger.info(f"LanceDB загружен: {self.recommender.table_name}")
            self.recommender.update_weights(
                text_weight=1.0,
                genre_weight=1.0,
                theme_weight=0.8,
                demographic_weight=0.5
            )
        except Exception as e:
            logger.warning(f"Таблица не найдена: {e}")

    async def recommend_by_text(self, query: str, limit: int, min_score: float) -> tuple[List[Dict], float]:
        """Поиск похожих аниме по тексту"""
        start_time = time.time()

        if self.recommender is None or self.recommender.table is None:
            raise ValueError("Recommender not loaded")

        results = self.recommender.find_similar_by_text(query, limit=limit, min_score=min_score)
        processing_time = (time.time() - start_time) * 1000

        return results, processing_time

    async def recommend_by_anime_id(
            self,
            anime_id: int,
            limit: int,
            min_score: float,
            text_weight: float,
            genre_weight: float,
            theme_weight: float,
            demo_weight: float
    ) -> tuple[List[Dict], float]:
        """Поиск похожих аниме по ID"""
        start_time = time.time()

        if self.recommender is None or self.recommender.table is None:
            raise ValueError("Recommender not loaded")

        self.recommender.update_weights(
            text_weight=text_weight,
            genre_weight=genre_weight,
            theme_weight=theme_weight,
            demographic_weight=demo_weight
        )

        results = self.recommender.find_similar_by_id(anime_id, limit=limit, min_score=min_score)
        processing_time = (time.time() - start_time) * 1000

        return results, processing_time

    async def get_weights(self) -> Dict[str, float]:
        """Получить текущие веса"""
        if self.recommender is None:
            raise ValueError("Recommender not loaded")
        return self.recommender.weights