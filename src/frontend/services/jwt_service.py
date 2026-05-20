import jwt
from fastapi import Request
from src.frontend.config.settings import settings

#   Такой Claims на сервисе авторизации
#   type Claims struct {
#	    JwtID  uuid.UUID `json:"jwt_id"`
#	    UserID uuid.UUID `json:"user_id"`
#	    Email  string    `json:"email"`
#	    Role   string    `json:"role"`
#	    jwt.RegisteredClaims
#   }

class JWTService:

    def get_token_from_cookie(self, request: Request) -> str | None:
        return request.cookies.get("access_token")

    def _parse_local(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return None

    async def verify(self, request: Request) -> tuple[dict, bool]:
        """
        Возвращает (payload, needs_refresh).
        needs_refresh — True если access_token истёк/отсутствует, надо редиректить на /refresh
        """
        token = self.get_token_from_cookie(request)

        if not token:
            return {}, True

        payload = self._parse_local(token)
        if payload is not None:
            return payload, False

        return {}, True


jwt_service = JWTService()