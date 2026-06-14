#!/usr/bin/env python
"""Скрипт для обучения Implicit ALS модели коллаборативной фильтрации"""

import sys
import logging
from pathlib import Path
import traceback

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.recommendation_service.recommenders.collaborative import ImplicitRecommender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Training Collaborative Filtering Model (Implicit ALS)")
    logger.info("Based on user favorites (implicit feedback)")

    FACTORS = 50
    ITERATIONS = 20
    REGULARIZATION = 0.01
    MIN_FAVORITES = 1

    logger.info(f"Parameters:")
    logger.info(f"  - Factors: {FACTORS}")
    logger.info(f"  - Iterations: {ITERATIONS}")
    logger.info(f"  - Regularization: {REGULARIZATION}")
    logger.info(f"  - Min favorites per user: {MIN_FAVORITES}")

    logger.info("Loading user favorites")

    recommender = ImplicitRecommender(
        factors=FACTORS,
        iterations=ITERATIONS,
        regularization=REGULARIZATION
    )

    try:
        user_ids, anime_ids = recommender.load_favorites(min_favorites=MIN_FAVORITES)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return

    logger.info("Training ALS model")

    try:
        stats = recommender.fit(user_ids, anime_ids)
        logger.info(f"Training completed!")
        logger.info(f"  - Users: {stats['n_users']}")
        logger.info(f"  - Anime: {stats['n_anime']}")
        logger.info(f"  - Factors: {stats['n_factors']}")
        logger.info(f"  - Iterations: {stats['n_iterations']}")
        logger.info(f"  - Total interactions: {stats['n_interactions']}")
    except Exception as e:
        logger.error(f"Error training model: {e}")
        traceback.print_exc()
        return

    logger.info("Saving model")

    model_path = Path(__file__).parent.parent / "ml_files" / "implicit_als_model.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)

    recommender.save_model(str(model_path))

    logger.info("Training completed successfully!")
    logger.info(f"Model saved to: {model_path}")


if __name__ == "__main__":
    main()