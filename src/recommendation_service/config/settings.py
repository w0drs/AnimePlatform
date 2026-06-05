from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    env: str = os.getenv("ENV", "development")

    # API endpoints
    anime_service: str = os.getenv("ANIME_SERVICE_ENDPOINT", "http://localhost:8001")
    recommendation_port: int = int(os.getenv("RECOMMENDS_PORT", 8003))

    # LanceDB
    lance_db_path: str = os.getenv("LANCE_DB_PATH", "src/recommendation_service/lancedb")
    lance_table_name: str = os.getenv("LANCE_TABLE_NAME", "anime_embeddings")

    # Model
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # PostgreSQL
    pg_host: str = os.getenv("PG_HOST", "192.168.3.160")
    pg_port: int = int(os.getenv("PG_PORT", 5432))
    pg_database: str = os.getenv("PG_DATABASE", "kuronami")
    pg_user: str = os.getenv("PG_USER", "postgres")
    pg_password: str = os.getenv("PG_PASSWORD", "postgres")

    @property
    def pg_params(self) -> dict:
        """Параметры для psycopg2"""
        return {
            "host": self.pg_host,
            "port": self.pg_port,
            "database": self.pg_database,
            "user": self.pg_user,
            "password": self.pg_password
        }

    @property
    def pg_dsn(self) -> str:
        """DSN для SQLAlchemy"""
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()