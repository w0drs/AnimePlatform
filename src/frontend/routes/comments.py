from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
import httpx

from src.frontend.services.anime_service import anime_service
from src.frontend.config.settings import settings
from src.frontend.schemas.comments import CommentCreate
from src.frontend.services.auth_decorator import require_auth

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.globals.update(max=max, min=min)

# API роуты для комментариев
@router.post("/api/comments/add", name="api_add_comment")
async def api_add_comment(request: Request, comment: CommentCreate):
    print(comment)
    access_token = request.cookies.get("access_token")
    if not access_token:
        return {"success": False, "error": "not authorized"}
    body = {"text": comment.text, "anime_id": comment.anime_id}
    if comment.tagged_user_id:
        body["tagged_user_id"] = comment.tagged_user_id

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.comments_service}/comments/anime/",
                headers={"Authorization": f"Bearer {access_token}"},
                json=body,
            )
        except httpx.RequestError:
            return {"success": False, "error": "service unavailable"}

    if response.status_code not in (200, 201):
        return {"success": False, "error": "error to create comment"}

    return {"success": True}

# Комментарии с пагинацией
@router.get("/anime/{anime_id}/comments")
async def anime_comments(request: Request, anime_id: str, page: int = 1):
    limit = 10
    comments_raw = await anime_service.get_comments(anime_id, page=page)
    comments = await anime_service.enrich_comments(comments_raw)

    return templates.TemplateResponse("anime_comments_partial.html", {
        "request": request,
        "anime_id": anime_id,
        "comments": comments,
        "page": page,
        "has_next": len(comments) == limit,
        "has_prev": page > 1,
    })
