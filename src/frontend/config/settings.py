from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Внутренняя система, к чему узер не сможет получить доступ
    anime_service: str = "http://192.168.3.92:8001"
    news_service: str = "http://192.168.3.92:8001"

    auth_service: str = "http://192.168.3.92:8002"
    favorite_service: str = "http://192.168.3.92:8002"
    comments_service: str = "http://192.168.3.92:8002"

    frontend_port: int = 8000
    frontend_host: str = "0.0.0.0"

    s3_access_key: str = ""
    s3_secret_key: str = ""
    images_bucket: str = "kuronami-images"
    anime_bucket: str = "discipline"

    # Что на фронт идет (в html вставляется или что-то такое, что на пк юзера выполнится)
    images_bucket_link: str = f"https://kuronami-images.storage.yandexcloud.net"
    anime_bucket_link: str = f"https://discipline.storage.yandexcloud.net"

    default_user_icon_name: str = f"{images_bucket_link}/default1.png"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()