#!/usr/bin/env python
"""Скрипт генерации коллаборативных рекомендаций и сохранения в БД"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.recommendation_service.recommenders.collaborative import ImplicitRecommender
from src.recommendation_service.config.settings import settings
import psycopg2
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

N_RECOMMENDATIONS_PER_USER = 20


def main():
    logger.info("Generating Collaborative Recommendations")

    model_path = Path(__file__).parent.parent / "ml_files" / "implicit_als_model.pkl"

    if not model_path.exists():
        logger.error(f"Модель не найдена: {model_path}")
        logger.info("Сначала обучите модель: python -m src.recommendation_service.scripts.train_collaborative")
        return

    # Загружаем модель
    logger.info("Загрузка модели")
    recommender = ImplicitRecommender()
    recommender.load_model(str(model_path))

    # Получаем всех пользователей
    logger.info("Получение пользователей")
    conn = psycopg2.connect(**settings.pg_params)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT user_id FROM favorites")
    users = [row[0] for row in cur.fetchall()]
    cur.close()
    logger.info(f"Найдено {len(users)} пользователей")

    if not users:
        logger.warning("Нет пользователей для генерации рекомендаций")
        return

    logger.info("Генерация рекомендаций")

    # Очищаем старые рекомендации
    cur = conn.cursor()
    cur.execute("TRUNCATE collaborative_recommendations")

    total_inserted = 0
    data_to_insert = []

    for i, user_id in enumerate(users):
        logger.info(f"Пользователь {i + 1}/{len(users)}: {user_id}")

        try:
            recs = recommender.get_user_recommendations(str(user_id), N_RECOMMENDATIONS_PER_USER)

            for rec in recs:
                data_to_insert.append((str(user_id), rec['id']))

            # Вставляем батчами каждые 500 записей
            if len(data_to_insert) >= 500:
                execute_values(cur, """
                    INSERT INTO collaborative_recommendations (user_id, anime_id)
                    VALUES %s
                """, data_to_insert)
                total_inserted += len(data_to_insert)
                logger.info(f"  Сохранено {total_inserted} рекомендаций")
                data_to_insert = []

        except Exception as e:
            logger.error(f"Ошибка для {user_id}: {e}")

    # Вставляем остатки
    if data_to_insert:
        execute_values(cur, """
            INSERT INTO collaborative_recommendations (user_id, anime_id)
            VALUES %s
        """, data_to_insert)
        total_inserted += len(data_to_insert)

    conn.commit()
    cur.close()
    conn.close()

    logger.info(f"Сохранено {total_inserted} рекомендаций для {len(users)} пользователей")


if __name__ == "__main__":
    main()