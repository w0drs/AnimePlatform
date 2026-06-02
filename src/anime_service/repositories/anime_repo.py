import json
from typing import Optional, List, Dict
from src.anime_service.database.connection import db


class AnimeRepository:

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
                SELECT id, title_english, image_webp_large_url, trailer_url, 
                       type, episodes, duration, rating, synopsis, background, year
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
                ORDER BY g.name
            """, (anime_id,))
            anime['genres'] = [row['name'] for row in cur.fetchall()]

            # Темы
            cur.execute("""
                SELECT t.name
                FROM themes t
                JOIN anime_themes at ON t.id = at.theme_id
                WHERE at.anime_id = %s
                ORDER BY t.name
            """, (anime_id,))
            themes_rows = cur.fetchall()
            anime['themes'] = [row['name'] for row in themes_rows]

            # Демографика
            cur.execute("""
                SELECT d.name
                FROM demographics d
                JOIN anime_demographics ad ON d.id = ad.demographic_id
                WHERE ad.anime_id = %s
                ORDER BY d.name
            """, (anime_id,))
            demo_rows = cur.fetchall()
            anime['demographics'] = [row['name'] for row in demo_rows]

            # Студии
            cur.execute("""
                SELECT s.name
                FROM studios s
                JOIN anime_studios a_st ON s.id = a_st.studio_id
                WHERE a_st.anime_id = %s
                ORDER BY s.name
            """, (anime_id,))
            studios_rows = cur.fetchall()
            anime['studios'] = [row['name'] for row in studios_rows]
            return anime

    @staticmethod
    def get_by_ids(ids: List[int]) -> List[Dict]:
        """Получить аниме по списку ID (оптимизированная версия)"""
        if not ids:
            return []

        placeholders = ','.join(['%s'] * len(ids))
        with db.get_cursor() as cur:
            cur.execute(f"""
                SELECT 
                    a.id, a.title_english, a.image_webp_large_url, a.type, 
                    a.episodes, a.duration, a.rating, a.synopsis, a.year,
                    COALESCE(
                        (SELECT json_agg(DISTINCT g.name ORDER BY g.name)
                         FROM anime_genres ag 
                         JOIN genres g ON ag.genre_id = g.id 
                         WHERE ag.anime_id = a.id), '[]'
                    ) as genres,
                    COALESCE(
                        (SELECT json_agg(DISTINCT t.name ORDER BY t.name)
                         FROM anime_themes at 
                         JOIN themes t ON at.theme_id = t.id 
                         WHERE at.anime_id = a.id), '[]'
                    ) as themes,
                    COALESCE(
                        (SELECT json_agg(DISTINCT d.name ORDER BY d.name)
                         FROM anime_demographics ad 
                         JOIN demographics d ON ad.demographic_id = d.id 
                         WHERE ad.anime_id = a.id), '[]'
                    ) as demographics,
                    COALESCE(
                        (SELECT json_agg(DISTINCT s.name ORDER BY s.name)
                         FROM anime_studios a_st 
                         JOIN studios s ON a_st.studio_id = s.id 
                         WHERE a_st.anime_id = a.id), '[]'
                    ) as studios
                FROM anime a
                WHERE a.id IN ({placeholders})
                ORDER BY a.id
            """, ids)

            results = cur.fetchall()

            for row in results:
                if row.get('genres') and isinstance(row['genres'], str):
                    row['genres'] = json.loads(row['genres']) if row['genres'] != '[]' else []
                if row.get('themes') and isinstance(row['themes'], str):
                    row['themes'] = json.loads(row['themes']) if row['themes'] != '[]' else []
                if row.get('demographics') and isinstance(row['demographics'], str):
                    row['demographics'] = json.loads(row['demographics']) if row['demographics'] != '[]' else []
                if row.get('studios') and isinstance(row['studios'], str):
                    row['studios'] = json.loads(row['studios']) if row['studios'] != '[]' else []

            return results

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
        """Поиск аниме по названию"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT id, title_english, image_webp_large_url, type, episodes, rating, year
                FROM anime
                WHERE title_english ILIKE %s
                LIMIT %s
            """, (f'%{query}%', limit))
            return cur.fetchall()

    @staticmethod
    def filter_anime(
            limit: int = 20,
            offset: int = 0,
            year: Optional[int] = None,
            year_from: Optional[int] = None,
            year_to: Optional[int] = None,
            anime_type: Optional[str] = None,
            rating: Optional[str] = None,
            genre: Optional[str] = None,
            theme: Optional[str] = None,
            demographic: Optional[str] = None,
            studio: Optional[str] = None,
            search: Optional[str] = None
    ) -> tuple[List[Dict], int]:
        """
        Фильтрация аниме с пагинацией (оптимизированная версия, 1 запрос)
        """
        with db.get_cursor() as cur:
            # ============= 1. Базовый запрос для фильтрации ID =============
            filter_query = """
                SELECT DISTINCT a.id
                FROM anime a
                LEFT JOIN anime_genres ag ON a.id = ag.anime_id
                LEFT JOIN genres g ON ag.genre_id = g.id
                LEFT JOIN anime_themes at ON a.id = at.anime_id
                LEFT JOIN themes t ON at.theme_id = t.id
                LEFT JOIN anime_demographics ad ON a.id = ad.anime_id
                LEFT JOIN demographics d ON ad.demographic_id = d.id
                LEFT JOIN anime_studios a_st ON a.id = a_st.anime_id
                LEFT JOIN studios s ON a_st.studio_id = s.id
                WHERE 1=1
            """
            params = []

            # Год
            if year:
                filter_query += " AND a.year = %s"
                params.append(year)
            if year_from:
                filter_query += " AND a.year >= %s"
                params.append(year_from)
            if year_to:
                filter_query += " AND a.year <= %s"
                params.append(year_to)

            # Тип
            if anime_type:
                filter_query += " AND a.type = %s"
                params.append(anime_type)

            # Рейтинг
            if rating:
                filter_query += " AND a.rating = %s"
                params.append(rating)

            # Жанр
            if genre:
                filter_query += " AND g.name = %s"
                params.append(genre)

            # Тема
            if theme:
                filter_query += " AND t.name = %s"
                params.append(theme)

            # Демографика
            if demographic:
                filter_query += " AND d.name = %s"
                params.append(demographic)

            # Студия
            if studio:
                filter_query += " AND s.name = %s"
                params.append(studio)

            # Поиск по названию
            if search:
                filter_query += " AND a.title_english ILIKE %s"
                params.append(f"%{search}%")

            # ============= 2. Подсчет общего количества =============
            count_query = f"SELECT COUNT(*) as total FROM ({filter_query}) as filtered"
            cur.execute(count_query, params)
            total = cur.fetchone()['total']

            if total == 0:
                return [], 0

            # ============= 3. Получаем ID с пагинацией =============
            filter_query += " ORDER BY a.id LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(f"""
                SELECT a.id
                FROM anime a
                WHERE a.id IN ({filter_query})
                ORDER BY a.id
            """, params)

            anime_ids = [row['id'] for row in cur.fetchall()]

            if not anime_ids:
                return [], 0

            # ============= 4. ОДНИМ ЗАПРОСОМ получаем все данные =============
            placeholders = ','.join(['%s'] * len(anime_ids))

            cur.execute(f"""
                SELECT 
                    a.id, 
                    a.title_english, 
                    a.image_webp_large_url, 
                    a.type, 
                    a.episodes, 
                    a.duration, 
                    a.rating, 
                    a.synopsis, 
                    a.year,
                    COALESCE(
                        (SELECT json_agg(DISTINCT g.name ORDER BY g.name)
                         FROM anime_genres ag 
                         JOIN genres g ON ag.genre_id = g.id 
                         WHERE ag.anime_id = a.id), '[]'
                    ) as genres,
                    COALESCE(
                        (SELECT json_agg(DISTINCT t.name ORDER BY t.name)
                         FROM anime_themes at 
                         JOIN themes t ON at.theme_id = t.id 
                         WHERE at.anime_id = a.id), '[]'
                    ) as themes,
                    COALESCE(
                        (SELECT json_agg(DISTINCT d.name ORDER BY d.name)
                         FROM anime_demographics ad 
                         JOIN demographics d ON ad.demographic_id = d.id 
                         WHERE ad.anime_id = a.id), '[]'
                    ) as demographics,
                    COALESCE(
                        (SELECT json_agg(DISTINCT s.name ORDER BY s.name)
                         FROM anime_studios a_st 
                         JOIN studios s ON a_st.studio_id = s.id 
                         WHERE a_st.anime_id = a.id), '[]'
                    ) as studios
                FROM anime a
                WHERE a.id IN ({placeholders})
                ORDER BY a.id
            """, anime_ids)

            results = cur.fetchall()

            # Преобразуем JSON строки в списки Python
            for row in results:
                if row.get('genres') and isinstance(row['genres'], str):
                    row['genres'] = json.loads(row['genres']) if row['genres'] != '[]' else []
                if row.get('themes') and isinstance(row['themes'], str):
                    row['themes'] = json.loads(row['themes']) if row['themes'] != '[]' else []
                if row.get('demographics') and isinstance(row['demographics'], str):
                    row['demographics'] = json.loads(row['demographics']) if row['demographics'] != '[]' else []
                if row.get('studios') and isinstance(row['studios'], str):
                    row['studios'] = json.loads(row['studios']) if row['studios'] != '[]' else []

            return results, total

    @staticmethod
    def get_genres_by_anime_id(anime_id: int) -> List[str]:
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT g.name
                FROM genres g
                JOIN anime_genres ag ON g.id = ag.genre_id
                WHERE ag.anime_id = %s
                ORDER BY g.name
            """, (anime_id,))
            return [row['name'] for row in cur.fetchall()]

    @staticmethod
    def get_themes_by_anime_id(anime_id: int) -> List[str]:
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT t.name
                FROM themes t
                JOIN anime_themes at ON t.id = at.theme_id
                WHERE at.anime_id = %s
                ORDER BY t.name
            """, (anime_id,))
            return [row['name'] for row in cur.fetchall()]

    @staticmethod
    def get_demographics_by_anime_id(anime_id: int) -> List[str]:
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT d.name
                FROM demographics d
                JOIN anime_demographics ad ON d.id = ad.demographic_id
                WHERE ad.anime_id = %s
                ORDER BY d.name
            """, (anime_id,))
            return [row['name'] for row in cur.fetchall()]

    @staticmethod
    def get_studios_by_anime_id(anime_id: int) -> List[str]:
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT s.name
                FROM studios s
                JOIN anime_studios as2 ON s.id = as2.studio_id
                WHERE as2.anime_id = %s
                ORDER BY s.name
            """, (anime_id,))
            return [row['name'] for row in cur.fetchall()]