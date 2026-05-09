import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from src.anime_service.config.settings import settings


class Database:
    def __init__(self):
        self.conn_params = {
            'host': settings.pg_host,
            'port': settings.pg_port,
            'database': settings.pg_database,
            'user': settings.pg_user,
            'password': settings.pg_password
        }

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = psycopg2.connect(**self.conn_params)
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Контекстный менеджер для курсора с dict результатами"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=cursor_factory) as cur:
                yield cur
                conn.commit()


db = Database()