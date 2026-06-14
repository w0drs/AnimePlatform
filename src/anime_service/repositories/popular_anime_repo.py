from typing import Optional, List, Dict
from src.anime_service.database.connection import db


class PopularAnimeRepository:
    @staticmethod
    def get_all(limit: int = 50, offset: int = 0) -> List[Dict]:
        """Получить все популярные аниме с пагинацией"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, anime_id, large_poster_url, created_at, updated_at
                FROM popular_anime
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()

    @staticmethod
    def get_by_id(popular_id: int) -> Optional[Dict]:
        """Получить запись популярного аниме по ID"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, anime_id, large_poster_url, created_at, updated_at
                FROM popular_anime
                WHERE id = %s
            """, (popular_id,))
            return cur.fetchone()

    @staticmethod
    def get_by_anime_id(anime_id: int) -> Optional[Dict]:
        """Получить запись популярного аниме по anime_id"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, anime_id, large_poster_url, created_at, updated_at
                FROM popular_anime
                WHERE anime_id = %s
            """, (anime_id,))
            return cur.fetchone()

    @staticmethod
    def get_popular_with_anime_details(limit: int = 50, offset: int = 0) -> List[Dict]:
        """Получить популярные аниме с базовой информацией об аниме"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT 
                    pa.id as popular_id,
                    pa.large_poster_url,
                    pa.created_at as popular_created_at,
                    a.id as anime_id,
                    a.title_english,
                    a.image_webp_large_url,
                    a.type,
                    a.episodes,
                    a.duration,
                    a.rating,
                    a.synopsis,
                    a.year
                FROM popular_anime pa
                JOIN anime a ON pa.anime_id = a.id
                ORDER BY pa.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()

    @staticmethod
    def get_popular_with_full_details(limit: int = 50, offset: int = 0) -> List[Dict]:
        """Получить популярные аниме с полной детализацией (жанры, темы, студии)"""
        with db.get_cursor() as cur:
            # Получаем основную информацию
            cur.execute("""
                SELECT 
                    pa.id as popular_id,
                    pa.large_poster_url,
                    a.id as anime_id,
                    a.title_english,
                    a.image_webp_large_url,
                    a.trailer_url,
                    a.type,
                    a.episodes,
                    a.duration,
                    a.rating,
                    a.synopsis,
                    a.background,
                    a.year
                FROM popular_anime pa
                JOIN anime a ON pa.anime_id = a.id
                ORDER BY pa.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))

            popular_anime_list = cur.fetchall()

            # Для каждого аниме подгружаем дополнительные данные
            for popular in popular_anime_list:
                anime_id = popular['anime_id']

                # Жанры
                cur.execute("""
                    SELECT g.name
                    FROM genres g
                    JOIN anime_genres ag ON g.id = ag.genre_id
                    WHERE ag.anime_id = %s
                """, (anime_id,))
                popular['genres'] = [row['name'] for row in cur.fetchall()]

                # Темы
                cur.execute("""
                    SELECT t.name
                    FROM themes t
                    JOIN anime_themes at ON t.id = at.theme_id
                    WHERE at.anime_id = %s
                """, (anime_id,))
                popular['themes'] = [row['name'] for row in cur.fetchall()]

                # Демографика
                cur.execute("""
                    SELECT d.name
                    FROM demographics d
                    JOIN anime_demographics ad ON d.id = ad.demographic_id
                    WHERE ad.anime_id = %s
                """, (anime_id,))
                popular['demographics'] = [row['name'] for row in cur.fetchall()]

                # Студии
                cur.execute("""
                    SELECT s.name
                    FROM studios s
                    JOIN anime_studios as2 ON s.id = as2.studio_id
                    WHERE as2.anime_id = %s
                """, (anime_id,))
                popular['studios'] = [row['name'] for row in cur.fetchall()]

            return popular_anime_list

    @staticmethod
    def create(data: Dict) -> int:
        """Добавить аниме в популярные"""
        with db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO popular_anime (anime_id, large_poster_url)
                VALUES (%(anime_id)s, %(large_poster_url)s)
                ON CONFLICT (anime_id) DO UPDATE SET
                    large_poster_url = EXCLUDED.large_poster_url,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, data)
            return cur.fetchone()['id']

    @staticmethod
    def update(popular_id: int, data: Dict) -> bool:
        """Обновить запись популярного аниме"""
        set_parts = []
        values = []

        for key, value in data.items():
            if value is not None:
                set_parts.append(f"{key} = %s")
                values.append(value)

        if not set_parts:
            return False

        values.append(popular_id)
        query = f"""
            UPDATE popular_anime 
            SET {', '.join(set_parts)}
            WHERE id = %s
            RETURNING id
        """

        with db.get_cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone() is not None

    @staticmethod
    def delete(popular_id: int) -> bool:
        """Удалить запись из популярных"""
        with db.get_cursor() as cur:
            cur.execute("DELETE FROM popular_anime WHERE id = %s RETURNING id", (popular_id,))
            return cur.fetchone() is not None

    @staticmethod
    def delete_by_anime_id(anime_id: int) -> bool:
        """Удалить аниме из популярных по anime_id"""
        with db.get_cursor() as cur:
            cur.execute("DELETE FROM popular_anime WHERE anime_id = %s RETURNING id", (anime_id,))
            return cur.fetchone() is not None

    @staticmethod
    def count() -> int:
        """Подсчитать количество популярных аниме"""
        with db.get_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM popular_anime")
            return cur.fetchone()['count']
