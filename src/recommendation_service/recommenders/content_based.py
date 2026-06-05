import lancedb
import pandas as pd
import psycopg2
import logging
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from src.recommendation_service.config.settings import settings

logger = logging.getLogger(__name__)


class LanceRecommender:
    """Аниме рекомендер на LanceDB"""

    def __init__(self) -> None:
        self.db = lancedb.connect(settings.lance_db_path)
        self.model = SentenceTransformer(settings.embedding_model)
        self.table_name = settings.lance_table_name
        self.table = None

    def create_index(self, df: pd.DataFrame, batch_size: int = 1000) -> int:
        """Создает индекс из DataFrame с колонками id, synopsis, title_english"""
        embeddings = []
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            batch_embeddings = self.model.encode(batch['synopsis'].tolist())
            embeddings.extend(batch_embeddings)

        df_emb = df.copy()
        df_emb['vector'] = embeddings
        df_emb = df_emb[['id', 'title_english', 'vector']]

        self.table = self.db.create_table(self.table_name, df_emb, mode="overwrite")
        self.table.create_index(num_partitions=256, num_sub_vectors=96)

        return len(df_emb)

    def sync_from_postgres(self) -> int:
        """Синхронизирует данные из PostgreSQL"""
        conn = psycopg2.connect(**settings.pg_params)

        df = pd.read_sql("""
            SELECT id, title_english, synopsis 
            FROM anime 
            WHERE synopsis IS NOT NULL AND synopsis != ''
        """, conn)

        conn.close()

        if len(df) == 0:
            raise ValueError("Нет аниме с синопсисами")

        logger.info(f"Загружено {len(df)} аниме из PostgreSQL")
        return self.create_index(df)

    def find_similar(self, query: str, limit: int = 10, min_score: float = 0.3) -> List[Dict[str, Any]]:
        """Поиск похожих аниме по тексту"""
        if self.table is None:
            self.table = self.db.open_table(self.table_name)

        query_vec = self.model.encode(query)
        results = self.table.search(query_vec).limit(limit).to_pandas()

        results = results[results['_distance'] <= (1 - min_score)]
        results['similarity'] = 1 - results['_distance']
        results['title_english'] = results['title_english'].fillna('Unknown')

        return results[['id', 'title_english', 'similarity']].to_dict('records')

    def recommend_by_id(self, anime_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск похожих аниме по ID"""
        if self.table is None:
            self.table = self.db.open_table(self.table_name)

        anime_vec = self.table.search().where(f"id = {anime_id}").limit(1).to_pandas()

        if len(anime_vec) == 0:
            raise ValueError(f"Аниме с ID {anime_id} не найдено")

        results = self.table.search(anime_vec['vector'].iloc[0]).limit(limit + 1).to_pandas()
        results = results[results['id'] != anime_id].head(limit)
        results['similarity'] = 1 - results['_distance']
        results['title_english'] = results['title_english'].fillna('Unknown')

        return results[['id', 'title_english', 'similarity']].to_dict('records')