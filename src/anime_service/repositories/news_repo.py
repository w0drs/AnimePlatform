from typing import Optional, List, Dict
from src.anime_service.database.connection import db


class NewsRepository:
    """


    """
    @staticmethod
    def get_all(limit: int = 20, offset: int = 0, only_published: bool = True) -> List[Dict]:
        """Получить все новости с пагинацией"""
        with db.get_cursor() as cur:
            if only_published:
                cur.execute("""
                    SELECT id, title, slug, preview_text, preview_image_url, created_at, is_published
                    FROM news_preview
                    WHERE is_published = TRUE
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            else:
                cur.execute("""
                    SELECT id, title, slug, preview_text, preview_image_url, created_at, is_published
                    FROM news_preview
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            return cur.fetchall()

    @staticmethod
    def get_by_id(news_id: int) -> Optional[Dict]:
        """Получить новость по ID с полным содержанием"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT p.id, p.title, p.slug, p.preview_text, p.preview_image_url, 
                       p.created_at, p.is_published, c.full_content, c.full_image_url
                FROM news_preview p
                LEFT JOIN news_content c ON p.id = c.news_id
                WHERE p.id = %s
            """, (news_id,))
            return cur.fetchone()

    @staticmethod
    def get_by_slug(slug: str) -> Optional[Dict]:
        """Получить новость по slug"""
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT p.id, p.title, p.slug, p.preview_text, p.preview_image_url, 
                       p.created_at, p.is_published, c.full_content, c.full_image_url
                FROM news_preview p
                LEFT JOIN news_content c ON p.id = c.news_id
                WHERE p.slug = %s
            """, (slug,))
            return cur.fetchone()

    @staticmethod
    def create(data: Dict) -> int:
        """Создать новую новость"""
        with db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO news_preview (title, slug, preview_text, preview_image_url, is_published)
                VALUES (%(title)s, %(slug)s, %(preview_text)s, %(preview_image_url)s, %(is_published)s)
                RETURNING id
            """, data)
            news_id = cur.fetchone()['id']

            cur.execute("""
                INSERT INTO news_content (news_id, full_content, full_image_url)
                VALUES (%(news_id)s, %(full_content)s, %(full_image_url)s)
            """, {"news_id": news_id, "full_content": data.get("full_content"),
                  "full_image_url": data.get("full_image_url")})

            return news_id

    @staticmethod
    def update_preview(news_id: int, data: Dict) -> bool:
        """Обновить превью новости"""
        set_parts = []
        values = []
        for key, value in data.items():
            if value is not None and key in ['title', 'slug', 'preview_text', 'preview_image_url', 'is_published']:
                set_parts.append(f"{key} = %s")
                values.append(value)

        if not set_parts:
            return False

        values.append(news_id)
        query = f"""
            UPDATE news_preview 
            SET {', '.join(set_parts)}
            WHERE id = %s
            RETURNING id
        """

        with db.get_cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone() is not None

    @staticmethod
    def update_content(news_id: int, data: Dict) -> bool:
        """Обновить полное содержание новости"""
        set_parts = []
        values = []
        for key, value in data.items():
            if value is not None and key in ['full_content', 'full_image_url']:
                set_parts.append(f"{key} = %s")
                values.append(value)

        if not set_parts:
            return False

        values.append(news_id)
        query = f"""
            UPDATE news_content 
            SET {', '.join(set_parts)}
            WHERE news_id = %s
            RETURNING news_id
        """

        with db.get_cursor() as cur:
            cur.execute(query, values)
            return cur.fetchone() is not None

    @staticmethod
    def delete(news_id: int) -> bool:
        """Удалить новость (каскадно удалит и content)"""
        with db.get_cursor() as cur:
            cur.execute("DELETE FROM news_preview WHERE id = %s RETURNING id", (news_id,))
            return cur.fetchone() is not None

    @staticmethod
    def count(only_published: bool = True) -> int:
        """Подсчитать количество новостей"""
        with db.get_cursor() as cur:
            if only_published:
                cur.execute("SELECT COUNT(*) as count FROM news_preview WHERE is_published = TRUE")
            else:
                cur.execute("SELECT COUNT(*) as count FROM news_preview")
            return cur.fetchone()['count']

    @staticmethod
    def toggle_publish(news_id: int, is_published: bool) -> bool:
        """Переключить статус публикации"""
        with db.get_cursor() as cur:
            cur.execute("""
                UPDATE news_preview 
                SET is_published = %s 
                WHERE id = %s 
                RETURNING id
            """, (is_published, news_id))
            return cur.fetchone() is not None


