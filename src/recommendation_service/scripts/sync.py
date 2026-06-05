#!/usr/bin/env python
"""Скрипт синхронизации данных из PostgreSQL в LanceDB"""

import sys
import logging
from pathlib import Path
import os

# Меняем рабочую директорию на корень проекта
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from src.recommendation_service.recommenders.content_based import LanceRecommender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Синхронизация данных из PostgreSQL в LanceDB...")

    recommender = LanceRecommender()

    try:
        count = recommender.sync_from_postgres()
        logger.info(f"Синхронизация завершена! Загружено {count} аниме")
    except Exception as e:
        logger.error(f"Ошибка синхронизации: {e}")


if __name__ == "__main__":
    main()