from fastapi import APIRouter, Request
import httpx
from starlette.responses import JSONResponse

from src.frontend.config.settings import settings
from src.frontend.services.auth_decorator import require_auth

router = APIRouter()

@router.post("/api/favorites/{anime_id}")
@require_auth
async def add_favorite(request: Request, anime_id: int, payload: dict = None):
    access_token = request.cookies.get("access_token")
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.user_service}/user/favorites/{anime_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.RequestError:
            return JSONResponse({"success": False}, status_code=503)

    return JSONResponse({"success": response.status_code == 201})


@router.delete("/api/favorites/{anime_id}")
@require_auth
async def remove_favorite(request: Request, anime_id: int, payload: dict = None):
    access_token = request.cookies.get("access_token")
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{settings.user_service}/user/favorites/{anime_id}",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.RequestError:
            return JSONResponse({"success": False}, status_code=503)

    return JSONResponse({"success": True})