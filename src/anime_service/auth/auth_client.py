import httpx
from typing import Optional, Dict
from fastapi import Request
from src.anime_service.config.settings import settings


class AuthClient:
    """Клиент для взаимодействия с auth сервисом"""

    def __init__(self):
        self.auth_url = f"{settings.auth_host}:{settings.auth_port}/auth/check"

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Проверяет токен и возвращает данные пользователя"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.auth_url,
                    json={"access_token": token},
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                return None

            except Exception as e:
                return None

    def extract_token(self, request: Request) -> Optional[str]:
        """Извлекает токен из заголовка Authorization"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]


auth_client = AuthClient()