from typing import Optional, List, Dict
from src.anime_service.database.connection import db


class AnimeRepository:
    def __init__(self):
        ...

    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict]:
        """Получить все аниме с пагинацией"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, title_english, image_webp_large_url, type, episodes, duration, 
                       rating, synopsis, year
                FROM anime
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cur.fetchall()

    @staticmethod
    def get_by_id(anime_id: int) -> Optional[Dict]:
        """Получить аниме по ID"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, title_english, image_webp_large_url, type, episodes, duration, 
                       rating, synopsis, year
                FROM anime
                WHERE id = %s
            """, (anime_id,))
            return cur.fetchone()

    @staticmethod
    def get_details(anime_id: int) -> Optional[Dict]:
        """Получить аниме с жанрами, темами и студиями"""
        with db.get_cursor() as cur:
            # Основная информация
            cur.execute("""
                SELECT id, title_english, image_webp_large_url, trailer_url, type, episodes, duration, 
                       rating, synopsis, background, year
                FROM anime
                WHERE id = %s
            """, (anime_id,))
            anime = cur.fetchone()

            if not anime:
                return None

            # Жанры
            cur.execute("""
                SELECT g.name
                FROM genres g
                JOIN anime_genres ag ON g.id = ag.genre_id
                WHERE ag.anime_id = %s
            """, (anime_id,))
            anime['genres'] = [row['name'] for row in cur.fetchall()]

            # Темы
            cur.execute("""
                SELECT t.name
                FROM themes t
                JOIN anime_themes at ON t.id = at.theme_id
                WHERE at.anime_id = %s
            """, (anime_id,))
            anime['themes'] = [row['name'] for row in cur.fetchall()]

            # Демографика
            cur.execute("""
                SELECT d.name
                FROM demographics d
                JOIN anime_demographics ad ON d.id = ad.demographic_id
                WHERE ad.anime_id = %s
            """, (anime_id,))
            anime['demographics'] = [row['name'] for row in cur.fetchall()]

            # Студии
            cur.execute("""
                SELECT s.name
                FROM studios s
                JOIN anime_studios as2 ON s.id = as2.studio_id
                WHERE as2.anime_id = %s
            """, (anime_id,))
            anime['studios'] = [row['name'] for row in cur.fetchall()]

            return anime

    @staticmethod
    def create(data: Dict) -> int:
        """Создать новое аниме"""
        with db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO anime (
                    title_english, image_webp_large_url, trailer_url, type, episodes, 
                    duration, rating, synopsis, background, year
                ) VALUES (%(title_english)s, %(image_webp_large_url)s, %(trailer_url)s, 
                          %(type)s, %(episodes)s, %(duration)s, %(rating)s, 
                          %(synopsis)s, %(background)s, %(year)s)
                RETURNING id
            """, data)
            return cur.fetchone()['id']

    @staticmethod
    def update(anime_id: int, data: Dict) -> bool:
        """Обновить аниме"""
        set_parts = []
        values = []
        for key, value in data.items():
            if value is not None:
                set_parts.append(f"{key} = %s")
                values.append(value)

        if not set_parts:
            return False

        values.append(anime_id)
        query = f"""
            UPDATE anime 
            SET {', '.join(set_parts)}
            WHERE id = %s
            RETURNING id
        """

        with db.get_cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone() is not None

    @staticmethod
    def delete(anime_id: int) -> bool:
        """Удалить аниме"""
        with db.get_cursor() as cur:
            cur.execute("DELETE FROM anime WHERE id = %s RETURNING id", (anime_id,))
            return cur.fetchone() is not None

    @staticmethod
    def count() -> int:
        """Подсчитать количество аниме"""
        with db.get_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM anime")
            return cur.fetchone()['count']

    @staticmethod
    def search(query: str, limit: int = 20) -> List[Dict]:
        """Поиск аниме по названию или синопсису"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, title_english, image_webp_large_url, type, episodes, rating, year
                FROM anime
                WHERE title_english ILIKE %s OR synopsis ILIKE %s
                LIMIT %s
            """, (f'%{query}%', f'%{query}%', limit))
            return cur.fetchall()

    @staticmethod
    def filter_by_year(year: int, limit: int = 100) -> List[Dict]:
        """Фильтрация по году"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, title_english, image_webp_large_url, type, episodes, rating, year
                FROM anime
                WHERE year = %s
                ORDER BY title_english
                LIMIT %s
            """, (year, limit))
            return cur.fetchall()

    @staticmethod
    def get_all_with_filters(
            limit: int = 100,
            offset: int = 0,
            year: Optional[int] = None,
            type: Optional[str] = None,
            min_rating: Optional[str] = None
    ) -> List[Dict]:
        """Получить все аниме с фильтрацией и пагинацией"""
        with db.get_cursor() as cur:
            query = """
                SELECT id, title_english, image_webp_large_url, type, episodes, duration, 
                       rating, synopsis, year
                FROM anime
                WHERE 1=1
            """
            params = []

            if year:
                query += " AND year = %s"
                params.append(year)

            if type:
                query += " AND type = %s"
                params.append(type)

            if min_rating:
                query += " AND rating >= %s"
                params.append(min_rating)

            query += " ORDER BY id LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(query, params)
            return cur.fetchall()

    @staticmethod
    def get_by_ids(ids: List[int]) -> List[dict]:
        """Получить аниме по списку ID"""
        if not ids:
            return []

        placeholders = ','.join(['%s'] * len(ids))
        with db.get_cursor() as cur:
            query = f"""
                SELECT * FROM anime 
                WHERE id IN ({placeholders})
                ORDER BY id
            """
            cur.execute(query, ids)
            return cur.fetchall()