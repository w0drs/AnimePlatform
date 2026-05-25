from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    env: str = os.getenv("ENV", "development")

    # Внутренняя система, к чему узер не сможет получить доступ
    anime_service: str = os.getenv("ANIME_SERVICE_ENDPOINT", "http://localhost:8001")

    recommendation_port: int = int(os.getenv("RECOMMENDS_PORT", 8003))
    frontend_host: str = os.getenv("RECOMMENDS_ADDR", "localhost")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()