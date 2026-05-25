from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    env: str = os.getenv("ENV", "development")

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET", "jwt-secret")

    # Внутренняя система, к чему узер не сможет получить доступ
    anime_service: str = os.getenv("ANIME_SERVICE_ENDPOINT", "http://192.168.3.160:8001")
    news_service: str = os.getenv("NEWS_SERVICE_ENDPOINT", "http://192.168.3.160:8001")

    auth_service: str = os.getenv("AUTH_SERVICE_ENDPOINT", "http://192.168.3.106:8002")
    user_service: str = os.getenv("USER_SERVICE_ENDPOINT", "http://192.168.3.106:8002")
    comments_service: str = os.getenv("COMMENTS_SERVICE_ENDPOINT", "http://localhost:8002")

    frontend_port: int = int(os.getenv("FRONTEND_PORT", 8000))
    frontend_host: str = os.getenv("FRONTEND_ADDR", "0.0.0.0")

    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "")
    images_bucket: str = os.getenv("IMAGES_BUCKET", "kuronami-images")
    anime_bucket: str = os.getenv("ANIME_BUCKET", "discipline")

    # Что на фронт идет (в html вставляется или что-то такое, что на пк юзера выполнится)
    images_bucket_link: str = os.getenv("IMAGES_BUCKET_LINK", f"https://kuronami-images.storage.yandexcloud.net")
    anime_bucket_link: str = os.getenv("ANIME_BUCKET_LINK", f"https://discipline.storage.yandexcloud.net")

    default_user_icon_name: str = f"{images_bucket_link}/default1.jpg"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()