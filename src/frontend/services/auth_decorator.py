from functools import wraps
from fastapi import Request
from fastapi.responses import RedirectResponse
from src.frontend.services.jwt_service import jwt_service

def require_auth(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")

        payload, needs_refresh = await jwt_service.verify(request)
        if needs_refresh:
            path = request.url.path
            if request.cookies.get("refresh"):
                return RedirectResponse(url=f"/refresh?next={path}", status_code=302)

            kwargs["payload"] = {}
            return await func(*args, **kwargs)

        kwargs["payload"] = payload
        return await func(*args, **kwargs)

    return wrapper