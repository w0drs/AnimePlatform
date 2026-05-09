from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # PostgreSQL
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_database: str = "anime_db"
    pg_user: str = "postgres"
    pg_password: str = "12345"

    api_port: int = 8000
    api_host: str = "0.0.0.0"

    database_url: Optional[str] = None

    # LanceDB
    lance_db_path: str = "./lancedb"

    @property
    def pg_dsn(self) -> str:
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    @property
    def pg_params(self) -> dict:
        return {
            'host': self.pg_host,
            'port': self.pg_port,
            'database': self.pg_database,
            'user': self.pg_user,
            'password': self.pg_password
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # PG_HOST = pg_host


settings = Settings()