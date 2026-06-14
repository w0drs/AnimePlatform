import logging
from typing import List, Dict
from scipy.sparse import csr_matrix
import implicit
import pickle
import psycopg2
from src.recommendation_service.config.settings import settings

logger = logging.getLogger(__name__)


class ImplicitRecommender:
    """Коллаборативный рекомендер на основе Implicit Feedback (ALS)"""

    def __init__(self, factors: int = 50, iterations: int = 20, regularization: float = 0.01):
        self.factors = factors
        self.iterations = iterations
        self.regularization = regularization
        self.user_ids = None
        self.anime_ids = None
        self.user_map = None
        self.anime_map = None
        self.user_inv_map = None
        self.anime_inv_map = None
        self.model = None

    def load_favorites(self, min_favorites: int = 1):
        """Загружает избранное пользователей из БД"""

        conn = psycopg2.connect(**settings.pg_params)
        cur = conn.cursor()

        # Проверяем общее количество
        cur.execute("SELECT COUNT(*) FROM favorites")
        total = cur.fetchone()[0]
        logger.info(f"Всего записей в favorites: {total}")

        if total == 0:
            raise ValueError("Нет данных в таблице favorites")

        # Получаем пользователей с достаточным количеством избранного
        cur.execute("""
            SELECT user_id, anime_id
            FROM favorites
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            raise ValueError("Нет данных в таблице favorites")

        logger.info(f"Загружено {len(rows)} записей избранного")

        # Преобразуем в списки
        user_ids = []
        anime_ids = []
        for row in rows:
            user_ids.append(str(row[0]))
            anime_ids.append(row[1])

        logger.info(f"Уникальных пользователей: {len(set(user_ids))}")
        logger.info(f"Уникальных аниме: {len(set(anime_ids))}")

        return user_ids, anime_ids

    def prepare_matrix(self, user_ids: List[str], anime_ids: List[int]):
        """Подготавливает разреженную матрицу user-item"""
        self.user_ids = list(set(user_ids))
        self.anime_ids = list(set(anime_ids))

        self.user_map = {uid: i for i, uid in enumerate(self.user_ids)}
        self.anime_map = {aid: i for i, aid in enumerate(self.anime_ids)}
        self.user_inv_map = {i: uid for uid, i in self.user_map.items()}
        self.anime_inv_map = {i: aid for aid, i in self.anime_map.items()}

        rows = [self.user_map[uid] for uid in user_ids]
        cols = [self.anime_map[aid] for aid in anime_ids]
        data = [1.0] * len(rows)

        matrix = csr_matrix((data, (rows, cols)),
                            shape=(len(self.user_ids), len(self.anime_ids)))

        logger.info(f"Матрица: {matrix.shape}, ненулевых элементов: {matrix.nnz}")
        logger.info(f"Плотность: {matrix.nnz / (matrix.shape[0] * matrix.shape[1]) * 100:.4f}%")

        return matrix

    def fit(self, user_ids: List[str], anime_ids: List[int]) -> Dict:
        """Обучает модель Implicit ALS"""
        matrix = self.prepare_matrix(user_ids, anime_ids)

        self.model = implicit.als.AlternatingLeastSquares(
            factors=self.factors,
            iterations=self.iterations,
            regularization=self.regularization,
            random_state=42,
            calculate_training_loss=True
        )

        logger.info("Обучение модели ALS...")
        self.model.fit(matrix)

        return {
            "n_users": len(self.user_ids),
            "n_anime": len(self.anime_ids),
            "n_factors": self.factors,
            "n_iterations": self.iterations,
            "n_interactions": matrix.nnz
        }

    def get_user_recommendations(self, user_id: str, n_recommendations: int = 10) -> List[Dict]:
        """Рекомендации для пользователя"""
        if user_id not in self.user_map or self.model is None:
            return []

        user_idx = self.user_map[user_id]

        # Вычисляем scores как скалярное произведение
        user_vector = self.model.user_factors[user_idx]
        scores = user_vector.dot(self.model.item_factors.T)

        # Получаем топ-N индексов
        if hasattr(scores, 'toarray'):
            scores = scores.toarray().flatten()

        top_indices = scores.argsort()[-n_recommendations:][::-1]

        recommendations = []
        for idx in top_indices:
            score = scores[idx]
            anime_id = self.anime_inv_map.get(idx)
            if anime_id:
                recommendations.append({
                    "id": int(anime_id),
                    "title_english": "Unknown",
                    "similarity": float(score)
                })

        return recommendations

    def save_model(self, path: str):
        """Сохраняет модель"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'factors': self.factors,
                'iterations': self.iterations,
                'regularization': self.regularization,
                'user_ids': self.user_ids,
                'anime_ids': self.anime_ids,
                'user_map': self.user_map,
                'anime_map': self.anime_map,
                'user_inv_map': self.user_inv_map,
                'anime_inv_map': self.anime_inv_map
            }, f)
        logger.info(f"Модель сохранена в {path}")

    def load_model(self, path: str):
        """Загружает модель"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.factors = data['factors']
            self.iterations = data['iterations']
            self.regularization = data['regularization']
            self.user_ids = data['user_ids']
            self.anime_ids = data['anime_ids']
            self.user_map = data['user_map']
            self.anime_map = data['anime_map']
            self.user_inv_map = data['user_inv_map']
            self.anime_inv_map = data['anime_inv_map']
        logger.info(f"Модель загружена из {path}")