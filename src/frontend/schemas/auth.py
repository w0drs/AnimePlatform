from typing import Optional
from dataclasses import dataclass

@dataclass
class LoginResponse:
    """Ответ от auth сервиса при логине"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None

@dataclass
class ErrorResponse:
    """Ответ с ошибкой от auth сервиса"""
    error: str
    detail: Optional[str] = None
    status_code: int = 400

class AuthServiceError(Exception):
    """Кастомное исключение для ошибок auth сервиса"""
    def __init__(self, message: str, status_code: int = 500, detail: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)

