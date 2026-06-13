from pydantic_settings import BaseSettings
import os
from pathlib import Path


class Settings(BaseSettings):
    # PostgreSQL
    pg_host: str = os.getenv("PG_HOST", "192.168.3.160")
    pg_port: int = int(os.getenv("PG_PORT", 5432))
    pg_database: str = os.getenv("PG_DATABASE", "kuronami")
    pg_user: str = os.getenv("PG_USER", "postgres")
    pg_password: str = os.getenv("PG_PASSWORD", "postgres")

    # API
    anime_service: str = os.getenv("ANIME_SERVICE_ENDPOINT", "http://localhost:8001")
    recommendation_port: int = int(os.getenv("RECOMMENDS_PORT", 8003))

    # LanceDB
    lance_db_path: str = os.getenv("LANCE_DB_PATH", "src/recommendation_service/lancedb")
    lance_table_name: str = os.getenv("LANCE_TABLE_NAME", "anime_embeddings")

    # Model - правильный путь
    @property
    def embedding_model(self) -> str:
        """Возвращает абсолютный путь к модели"""
        model_path = os.getenv("EMBEDDING_MODEL", "models/all-MiniLM-L6-v2")
        if os.path.isabs(model_path):
            return model_path
        # Поднимаемся на 2 уровня вверх: config -> recommendation_service -> src
        base_dir = Path(__file__).resolve().parent.parent  # src/recommendation_service
        return str(base_dir / model_path)

    @property
    def pg_params(self) -> dict:
        return {
            "host": self.pg_host,
            "port": self.pg_port,
            "database": self.pg_database,
            "user": self.pg_user,
            "password": self.pg_password
        }

    @property
    def pg_dsn(self) -> str:
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()