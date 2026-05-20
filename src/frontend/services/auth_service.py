from src.frontend.schemas.auth import AuthServiceError, LoginResponse
from src.frontend.config.settings import settings

from typing import Optional, Dict, Any
import httpx

class AuthServiceClient:
    """Клиент для auth сервиса"""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    async def _request(
            self,
            method: str,
            path: str,
            json: Optional[Dict] = None,
            headers: Optional[Dict] = None,
            cookies: Optional[Dict] = None,
    ) -> tuple[httpx.Response, Dict[str, Any]]:
        """
        Базовый метод для отправки запросов.
        Возвращает (response, data) — чтобы вызывающий код мог читать куки.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{self.base_url}{path}",
                    json=json,
                    headers=headers or {},
                    cookies=cookies or {},
                )

                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {}

                if response.status_code >= 400:
                    error_msg = (
                        data.get("error")
                        or data.get("detail")
                        or f"HTTP {response.status_code}"
                    )
                    raise AuthServiceError(
                        message=error_msg,
                        status_code=response.status_code,
                        detail=data.get("detail") or data.get("error"),
                    )

                return response, data

            except httpx.TimeoutException:
                raise AuthServiceError(message="Service timeout", status_code=504)
            except httpx.RequestError as e:
                raise AuthServiceError(message=f"Service connection failed: {e}", status_code=503)

    @staticmethod
    def _extract_refresh_token(response: httpx.Response) -> Optional[str]:
        """Извлекает refresh_token из httponly куки ответа auth service."""
        return response.cookies.get("refresh") or response.cookies.get("refresh_token")

    async def login(
            self,
            email: str,
            password: str,
            client_ip: str,
            user_agent: str,
    ) -> LoginResponse:
        """
        Login user via auth service.

        Auth service возвращает:
          - access_token в теле ответа
          - refresh_token в httponly куке

        Args:
            email: User email
            password: User password
            client_ip: Client IP address
            user_agent: Client User-Agent

        Returns:
            LoginResponse с access_token и refresh_token

        Raises:
            AuthServiceError: If auth service returns error
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": user_agent,
            "X-Forwarded-For": client_ip,
            "X-Real-IP": client_ip,
        }

        response, data = await self._request(
            method="POST",
            path="/auth/login",
            json={"email": email, "password": password},
            headers=headers,
        )

        access_token = data.get("access_token")
        if not access_token:
            raise AuthServiceError(
                message="Invalid response from auth service: missing access_token",
                status_code=502,
            )

        return LoginResponse(
            access_token=access_token,
            refresh_token=self._extract_refresh_token(response),
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in"),
        )

    async def refresh(
            self,
            refresh_token: str,
            client_ip: str,
            user_agent: str,
    ) -> LoginResponse:
        """
        Refresh access token via auth service.

        Передаём refresh_token обратно auth service в куке (так, как он его выдал).
        Auth service возвращает новый access_token в теле и обновлённый refresh_token в httponly куке.

        Args:
            refresh_token: Значение куки refresh_token, сохранённое при login
            client_ip: Real client IP address
            user_agent: Client User-Agent header

        Returns:
            LoginResponse с новым access_token (и новым refresh_token если ротация)

        Raises:
            AuthServiceError: If auth service returns error
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": user_agent,
            "X-Forwarded-For": client_ip,
            "X-Real-IP": client_ip,
        }

        # Пробрасываем refresh_token именно в куке — auth service ждёт его там
        cookies = {"refresh": refresh_token}

        response, data = await self._request(
            method="POST",
            path="/auth/refresh",
            headers=headers,
            cookies=cookies,
        )

        access_token = data.get("access_token")
        if not access_token:
            raise AuthServiceError(
                message="Invalid response from auth service: missing access_token",
                status_code=502,
            )

        return LoginResponse(
            access_token=access_token,
            # Если auth service ротирует refresh_token — берём новый, иначе оставляем старый
            refresh_token=self._extract_refresh_token(response) or refresh_token,
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in"),
        )

    async def logout(
            self,
            access_token: str,
            client_ip: str,
    ) -> bool:
        """
        Logout user via auth service.

        Args:
            access_token: Current access token
            client_ip: Real client IP address

        Returns:
            True if logout successful
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-Forwarded-For": client_ip,
            "X-Real-IP": client_ip,
        }

        await self._request(method="POST", path="/auth/logout", headers=headers)
        return True

    async def validate_token(
            self,
            access_token: str,
            client_ip: str,
    ) -> Dict[str, Any]:
        """
        Validate access token with auth service.

        Args:
            access_token: Access token to validate
            client_ip: Real client IP address

        Returns:
            Dict with user info if token is valid
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Forwarded-For": client_ip,
            "X-Real-IP": client_ip,
        }

        _, data = await self._request(method="GET", path="/auth/validate", headers=headers)
        return data.get("user", {})

auth_service = AuthServiceClient(settings.auth_service)