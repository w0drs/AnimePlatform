from fastapi import HTTPException, Request, Depends, status
from typing import Optional, Dict
from src.anime_service.auth.auth_client import auth_client


# Роли пользователей
class UserRole:
    USER = "user"
    MODER = "moder"
    ADMIN = "admin"


# Какие роли имеют доступ к операциям
ROLE_PERMISSIONS = {
    "create_anime": [UserRole.MODER, UserRole.ADMIN],
    "update_anime": [UserRole.MODER, UserRole.ADMIN],
    "delete_anime": [UserRole.MODER, UserRole.ADMIN],
    "create_news": [UserRole.MODER, UserRole.ADMIN],
    "update_news": [UserRole.MODER, UserRole.ADMIN],
    "delete_news": [UserRole.MODER, UserRole.ADMIN],
    "publish_news": [UserRole.MODER, UserRole.ADMIN],
}


async def get_current_user(request: Request) -> Dict:
    """Получает текущего пользователя из токена"""
    token = auth_client.extract_token(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = await auth_client.verify_token(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data


async def get_current_user_optional(request: Request) -> Optional[Dict]:
    """Получает пользователя, если токен есть и валиден (для публичных эндпоинтов)"""
    token = auth_client.extract_token(request)
    if not token:
        return None

    return await auth_client.verify_token(token)


def require_role(required_roles: list):
    """Декоратор для проверки роли"""

    async def role_checker(user: Dict = Depends(get_current_user)):
        user_role = user.get("role")

        if not user_role or user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}, your role: {user_role}"
            )
        return user

    return role_checker


# Готовые зависимости для разных операций
require_admin = require_role([UserRole.ADMIN])
require_moder = require_role([UserRole.MODER, UserRole.ADMIN])
require_moder_or_admin = require_role([UserRole.MODER, UserRole.ADMIN])
