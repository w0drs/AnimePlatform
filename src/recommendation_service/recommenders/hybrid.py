import lancedb
import pandas as pd
import psycopg2
import logging
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from src.recommendation_service.config.settings import settings

logger = logging.getLogger(__name__)


def safe_set(value):
    """Безопасно преобразует значение в set"""
    if value is None:
        return set()
    if isinstance(value, (list, tuple)):
        return set(value)
    if hasattr(value, 'tolist'):
        return set(value.tolist())
    if isinstance(value, set):
        return value
    return {value} if value else set()


def safe_list(x):
    """Безопасно преобразует значение в список"""
    if x is None:
        return []
    if isinstance(x, float):
        return []
    if isinstance(x, (list, tuple)):
        return list(x)
    if hasattr(x, 'tolist'):
        return x.tolist()
    return [x] if x else []


class HybridRecommender:
    """
    Гибридный рекомендер аниме на основе:
    - Content-based (синопсис)
    - Совпадение жанров
    - Совпадение тем
    - Совпадение демографики
    - Фильтрация по возрастному рейтингу
    """

    # Порядок рейтингов (чем больше число, тем "строже" рейтинг)
    RATING_ORDER = {
        "G - All Ages": 0,
        "PG - Children": 1,
        "PG-13 - Teens 13 or older": 2,
        "R - 17+ (violence & profanity)": 3,
        "R+ - Mild Nudity": 4,
        "Rx - Hentai": 5
    }

    def __init__(self) -> None:
        self.db = lancedb.connect(settings.lance_db_path)
        self.model = SentenceTransformer(settings.embedding_model)
        self.table_name = settings.lance_table_name
        self.table = None

        # Веса для разных компонентов
        self.weights = {
            "text": 1.0,  # вес косинусной похожести описаний
            "genre": 1.0,  # вес совпадения жанров
            "theme": 1.0,  # вес совпадения тем
            "demographic": 1.0  # вес совпадения демографики
        }
        # Максимальное значение функции (0-4)
        self.max_score = 4.0

    def sync_from_postgres(self) -> int:
        """Синхронизирует данные из PostgreSQL (включая жанры, темы, демографику)"""
        conn = psycopg2.connect(**settings.pg_params)

        # Загружаем аниме с синопсисами
        df = pd.read_sql("""
            SELECT id, title_english, synopsis, rating
            FROM anime 
            WHERE synopsis IS NOT NULL AND synopsis != ''
        """, conn)

        # Загружаем жанры для каждого аниме
        genres_df = pd.read_sql("""
            SELECT a.id, COALESCE(array_agg(g.name), ARRAY[]::text[]) as genres
            FROM anime a
            LEFT JOIN anime_genres ag ON a.id = ag.anime_id
            LEFT JOIN genres g ON ag.genre_id = g.id
            GROUP BY a.id
        """, conn)

        # Загружаем темы
        themes_df = pd.read_sql("""
            SELECT a.id, COALESCE(array_agg(t.name), ARRAY[]::text[]) as themes
            FROM anime a
            LEFT JOIN anime_themes at ON a.id = at.anime_id
            LEFT JOIN themes t ON at.theme_id = t.id
            GROUP BY a.id
        """, conn)

        # Загружаем демографику
        demo_df = pd.read_sql("""
            SELECT a.id, COALESCE(array_agg(d.name), ARRAY[]::text[]) as demographics
            FROM anime a
            LEFT JOIN anime_demographics ad ON a.id = ad.anime_id
            LEFT JOIN demographics d ON ad.demographic_id = d.id
            GROUP BY a.id
        """, conn)

        conn.close()

        # Объединяем все данные
        df = df.merge(genres_df, on='id', how='left')
        df = df.merge(themes_df, on='id', how='left')
        df = df.merge(demo_df, on='id', how='left')

        # Заполняем NULL пустыми списками
        df['genres'] = df['genres'].apply(safe_list)
        df['themes'] = df['themes'].apply(safe_list)
        df['demographics'] = df['demographics'].apply(safe_list)

        # Генерируем эмбеддинги
        embeddings = []
        batch_size = 1000
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            batch_embeddings = self.model.encode(batch['synopsis'].tolist())
            embeddings.extend(batch_embeddings)

        df['vector'] = embeddings
        df_emb = df[['id', 'title_english', 'synopsis', 'rating',
                     'genres', 'themes', 'demographics', 'vector']]

        # Создаем таблицу
        self.table = self.db.create_table(self.table_name, df_emb, mode="overwrite")
        self.table.create_index(num_partitions=256, num_sub_vectors=96)

        logger.info(f"Создан индекс для {len(df_emb)} аниме")
        return len(df_emb)

    def _calculate_similarity_scores(self, target_anime: Dict, candidate_anime: Dict) -> Dict[str, float]:
        """Рассчитывает похожесть по каждому критерию"""

        # 1. Text similarity
        text_sim = 1.0 - target_anime.get('_distance', 1.0)

        # 2. Genre overlap
        target_genres = safe_set(target_anime.get('genres'))
        candidate_genres = safe_set(candidate_anime.get('genres'))
        if target_genres and candidate_genres:
            genre_overlap = len(target_genres & candidate_genres) / len(target_genres | candidate_genres)
        else:
            genre_overlap = 0.0

        # 3. Theme overlap
        target_themes = safe_set(target_anime.get('themes'))
        candidate_themes = safe_set(candidate_anime.get('themes'))
        if target_themes and candidate_themes:
            theme_overlap = len(target_themes & candidate_themes) / len(target_themes | candidate_themes)
        else:
            theme_overlap = 0.0

        # 4. Demographic overlap
        target_demo = safe_set(target_anime.get('demographics'))
        candidate_demo = safe_set(candidate_anime.get('demographics'))
        if target_demo and candidate_demo:
            demo_overlap = len(target_demo & candidate_demo) / len(target_demo | candidate_demo)
        else:
            demo_overlap = 0.0

        return {
            "text": text_sim,
            "genre": genre_overlap,
            "theme": theme_overlap,
            "demographic": demo_overlap
        }

    def _calculate_total_score(self, scores: Dict[str, float]) -> float:
        """Рассчитывает общий score (0-4)"""
        total = 0.0
        for key, weight in self.weights.items():
            total += scores.get(key, 0.0) * weight
        return min(total, self.max_score)

    def _is_rating_allowed(self, target_rating: Optional[str], candidate_rating: Optional[str]) -> bool:
        """Проверяет, можно ли показывать аниме с данным рейтингом"""
        if target_rating is None:
            return True

        target_level = self.RATING_ORDER.get(target_rating, 0)
        candidate_level = self.RATING_ORDER.get(candidate_rating, 0)

        # Не показываем аниме с более высоким рейтингом
        return candidate_level <= target_level

    def find_similar_by_id(self, anime_id: int, limit: int = 10, min_score: float = 0.5) -> List[Dict[str, Any]]:
        """Поиск похожих аниме по ID с учетом всех факторов"""
        if self.table is None:
            self.table = self.db.open_table(self.table_name)

        # Получаем вектор целевого аниме
        target_df = self.table.search().where(f"id = {anime_id}").limit(1).to_pandas()

        if len(target_df) == 0:
            raise ValueError(f"Аниме с ID {anime_id} не найдено")

        target_anime = target_df.iloc[0].to_dict()
        target_vector = target_anime['vector']
        target_rating = target_anime.get('rating')

        # Убираем _distance если есть (он не нужен для target)
        target_anime.pop('_distance', None)

        # Ищем кандидатов
        candidates_df = self.table.search(target_vector).limit(limit * 3).to_pandas()
        candidates_df = candidates_df[candidates_df['id'] != anime_id]

        results = []
        for _, row in candidates_df.iterrows():
            candidate = row.to_dict()

            # Извлекаем текстовую похожесть из _distance кандидата
            text_sim = 1.0 - float(candidate.get('_distance', 1.0))

            # Проверка рейтинга
            if not self._is_rating_allowed(target_rating, candidate.get('rating')):
                continue

            # Жанры
            target_genres = safe_set(target_anime.get('genres'))
            candidate_genres = safe_set(candidate.get('genres'))
            if target_genres and candidate_genres:
                genre_overlap = len(target_genres & candidate_genres) / len(target_genres | candidate_genres)
            else:
                genre_overlap = 0.0

            # Темы
            target_themes = safe_set(target_anime.get('themes'))
            candidate_themes = safe_set(candidate.get('themes'))
            if target_themes and candidate_themes:
                theme_overlap = len(target_themes & candidate_themes) / len(target_themes | candidate_themes)
            else:
                theme_overlap = 0.0

            # Демографика
            target_demo = safe_set(target_anime.get('demographics'))
            candidate_demo = safe_set(candidate.get('demographics'))
            if target_demo and candidate_demo:
                demo_overlap = len(target_demo & candidate_demo) / len(target_demo | candidate_demo)
            else:
                demo_overlap = 0.0

            # Общий score
            total_score = (
                text_sim * self.weights["text"] +
                genre_overlap * self.weights["genre"] +
                theme_overlap * self.weights["theme"] +
                demo_overlap * self.weights["demographic"]
            )
            total_score = min(total_score, self.max_score)

            if total_score >= min_score:
                results.append({
                    "id": int(candidate['id']),
                    "title_english": candidate.get('title_english', 'Unknown'),
                    "similarity": total_score,
                    "rating": candidate.get('rating')
                })

        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

    def find_similar_by_text(
            self,
            query: str,
            limit: int = 10,
            min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Поиск похожих аниме по тексту"""
        if self.table is None:
            self.table = self.db.open_table(self.table_name)

        query_vec = self.model.encode(query)
        results_df = self.table.search(query_vec).limit(limit).to_pandas()

        results_df['similarity'] = 1 - results_df['_distance']
        results_df['title_english'] = results_df['title_english'].fillna('Unknown')

        return results_df[['id', 'title_english', 'similarity']].to_dict('records')

    def update_weights(self, text_weight: float = 1.0, genre_weight: float = 1.0,
                       theme_weight: float = 1.0, demographic_weight: float = 1.0):
        """Обновляет веса компонентов"""
        self.weights = {
            "text": text_weight,
            "genre": genre_weight,
            "theme": theme_weight,
            "demographic": demographic_weight
        }
        logger.info(f"Weights updated: {self.weights}")