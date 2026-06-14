from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # PostgreSQL
    pg_host: str = os.getenv("PG_HOST", "192.168.3.160")
    pg_port: int = int(os.getenv("PG_PORT", 5432))
    pg_database: str = os.getenv("PG_DATABASE", "kuronami")
    pg_user: str = os.getenv("PG_USER", "postgres")
    pg_password: str = os.getenv("PG_PASSWORD", "postgres")

    api_port: int = int(os.getenv("API_PORT", 8001))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")

    auth_host: str = os.getenv("AUTH_HOST", "http://localhost")
    auth_port: int = int(os.getenv("AUTH_PORT", 8002))

    database_url: str = os.getenv("DATABASE_URL", "")

    # LanceDB
    lance_db_path: str = os.getenv("LANCE_DB_PATH", "./lancedb")

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


settings = Settings()