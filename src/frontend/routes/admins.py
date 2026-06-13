from fastapi import APIRouter, Request, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from pathlib import Path
from typing import Optional, List
from starlette.responses import JSONResponse

from src.frontend.services.auth_decorator import require_auth
from src.frontend.services.s3_service import upload_image
from src.frontend.config.settings import settings
from src.frontend.schemas.users import RoleUser, RoleKey, RoleMODER, RoleADMIN

BASE_DIR = Path(__file__).resolve().parent.parent
router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=BASE_DIR / "templates")

ANIME_API_URL = settings.anime_service

TOOLS = {
    "adminer":      settings.adminer_endpoint,
    "portainer":    settings.portainer_endpoint,
    "redisinsight": settings.redis_insight_endpoint,
    "anime_swagger": f"{settings.anime_service}/docs",
    "recommendation_swagger": f"{settings.recommends_service}/docs"
}

async def get_genres_list() -> List[tuple]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/genres", timeout=10.0)
        if response.status_code == 200:
            return [(g['id'], g['name']) for g in response.json()]
        return []


async def get_themes_list() -> List[tuple]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/themes", timeout=10.0)
        if response.status_code == 200:
            return [(t['id'], t['name']) for t in response.json()]
        return []


async def get_demographics_list() -> List[tuple]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/demographics", timeout=10.0)
        if response.status_code == 200:
            return [(d['id'], d['name']) for d in response.json()]
        return []


async def get_studios_list() -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/studios", timeout=10.0)
        if response.status_code == 200:
            return [s['name'] for s in response.json()]
        return []


async def get_anime_by_id(anime_id: int) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/{anime_id}", timeout=10.0)
        if response.status_code == 200:
            return response.json()
    return None



@router.get("", name="admin")
@require_auth
async def admin_page(request: Request, payload: dict = None):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        raise HTTPException(status_code=403)

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "active_page": "admin",
        "is_authorized": True,
        "is_admin": True,
    })


@router.get("/tools/{tool}")
@require_auth
async def admin_tool_redirect(request: Request, tool: str, payload: dict = None):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        raise HTTPException(status_code=403)

    url = TOOLS.get(tool)
    if not url:
        raise HTTPException(status_code=404)

    return RedirectResponse(url=url, status_code=302)

@router.get("/anime", response_class=HTMLResponse)
@require_auth
async def admin_anime_list(
        request: Request,
        page: int = 1,
        size: int = 20,
        payload: dict = None
):
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)
    if payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ANIME_API_URL}/anime/filter",
            params={"page": page, "size": size},
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()
            anime_list = data.get("items", [])
            total = data.get("total", 0)
            total_pages = data.get("pages", 0)
        else:
            anime_list = []
            total = 0
            total_pages = 0

    return templates.TemplateResponse("admin_anime_list.html", {
        "request": request,
        "is_authorized": True,
        "is_admin": True,
        "anime_list": anime_list,
        "total_pages": total_pages,
        "current_page": page,
        "title": "Manage Anime"
    })


@router.get("/anime/create", response_class=HTMLResponse)
@require_auth
async def admin_anime_create_form(
        request: Request,
        payload: dict = None
):
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)
    if payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    genres_list = await get_genres_list()
    themes_list = await get_themes_list()
    demographics_list = await get_demographics_list()
    studios_list = await get_studios_list()

    return templates.TemplateResponse("admin_anime_form.html", {
        "request": request,
        "is_authorized": True,
        "is_admin": True,
        "title": "Create Anime",
        "anime": None,
        "genres_list": genres_list,
        "themes_list": themes_list,
        "demographics_list": demographics_list,
        "studios_list": studios_list
    })


@router.post("/anime/create", response_class=HTMLResponse)
@require_auth
async def admin_anime_create(
        request: Request,
        title_english: str = Form(...),
        type: Optional[str] = Form(None),
        episodes: Optional[int] = Form(None),
        duration: Optional[str] = Form(None),
        rating: Optional[str] = Form(None),
        year: Optional[int] = Form(None),
        trailer_url: Optional[str] = Form(None),
        synopsis: Optional[str] = Form(None),
        background: Optional[str] = Form(None),
        genres: Optional[List[str]] = Form(None),
        themes: Optional[List[str]] = Form(None),
        demographics: Optional[List[str]] = Form(None),
        studios: Optional[str] = Form(None),
        poster_image: Optional[UploadFile] = File(None),
        payload: dict = None
):
    """Создание аниме с загрузкой изображения"""
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)
    if payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    # Загружаем изображение на S3 если оно есть
    image_url = None
    if poster_image and poster_image.filename:
        try:
            result = await upload_image(upload_type="anime", file=poster_image)
            image_url = result["url"]
        except Exception as e:
            return RedirectResponse(url="/admin/anime/create?error=Failed+to+upload+image", status_code=303)

    data = {
        "title_english": title_english,
        "type": type,
        "episodes": episodes,
        "duration": duration,
        "rating": rating,
        "year": year,
        "trailer_url": trailer_url,
        "synopsis": synopsis,
        "background": background,
        "genres": genres or [],
        "themes": themes or [],
        "demographics": demographics or [],
        "studios": studios.split(',') if studios else []
    }

    # Добавляем URL изображения если оно было загружено
    if image_url:
        data["image_webp_large_url"] = image_url

    # Убираем пустые значения
    data = {k: v for k, v in data.items() if v not in [None, "", []]}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ANIME_API_URL}/anime/",
            headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"},
            json=data,
            timeout=10.0
        )
        print(response.status_code)
        if response.status_code == 201:
            return RedirectResponse(url="/admin/anime", status_code=303)

    return RedirectResponse(url="/admin/anime/create?error=Failed+to+create+anime", status_code=303)


@router.get("/anime/{anime_id}/edit", response_class=HTMLResponse)
@require_auth
async def admin_anime_edit_form(
        request: Request,
        anime_id: int,
        payload: dict = None
):
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)
    if payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    anime = await get_anime_by_id(anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    genres_list = await get_genres_list()
    themes_list = await get_themes_list()
    demographics_list = await get_demographics_list()
    studios_list = await get_studios_list()

    return templates.TemplateResponse("admin_anime_form.html", {
        "request": request,
        "is_authorized": True,
        "is_admin": True,
        "title": f"Edit Anime — {anime.get('title_english', 'Untitled')}",
        "anime": anime,
        "genres_list": genres_list,
        "themes_list": themes_list,
        "demographics_list": demographics_list,
        "studios_list": studios_list
    })


@router.post("/anime/{anime_id}/edit", response_class=HTMLResponse)
@require_auth
async def admin_anime_edit(
        request: Request,
        anime_id: int,
        title_english: Optional[str] = Form(None),
        type: Optional[str] = Form(None),
        episodes: Optional[int] = Form(None),
        duration: Optional[str] = Form(None),
        rating: Optional[str] = Form(None),
        year: Optional[int] = Form(None),
        trailer_url: Optional[str] = Form(None),
        synopsis: Optional[str] = Form(None),
        background: Optional[str] = Form(None),
        genres: Optional[List[str]] = Form(None),
        themes: Optional[List[str]] = Form(None),
        demographics: Optional[List[str]] = Form(None),
        studios: Optional[str] = Form(None),
        poster_image: Optional[UploadFile] = File(None),
        payload: dict = None
):
    """Обновление аниме с возможностью загрузки нового изображения"""
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)
    if payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    # Загружаем новое изображение если оно есть
    image_url = None
    if poster_image and poster_image.filename:
        try:
            result = await upload_image(upload_type="anime", file=poster_image)
            image_url = result["url"]
        except Exception as e:
            return RedirectResponse(url=f"/admin/anime/{anime_id}/edit?error=Failed+to+upload+image", status_code=303)

    data = {
        "title_english": title_english,
        "type": type,
        "episodes": episodes,
        "duration": duration,
        "rating": rating,
        "year": year,
        "trailer_url": trailer_url,
        "synopsis": synopsis,
        "background": background,
        "genres": genres or [],
        "themes": themes or [],
        "demographics": demographics or [],
        "studios": studios.split(',') if studios else []
    }

    # Добавляем URL нового изображения если оно было загружено
    if image_url:
        data["image_webp_large_url"] = image_url

    # Убираем пустые значения
    data = {k: v for k, v in data.items() if v not in [None, "", []]}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{ANIME_API_URL}/anime/{anime_id}",
            json=data,
            timeout=10.0
        )

        if response.status_code == 200:
            return RedirectResponse(url="/admin/anime", status_code=303)

    return RedirectResponse(url=f"/admin/anime/{anime_id}/edit?error=Failed+to+update+anime", status_code=303)


@router.post("/anime/{anime_id}/delete", response_class=HTMLResponse)
@require_auth
async def admin_anime_delete(
        request: Request,
        anime_id: int,
        payload: dict = None
):
    if not payload:
        return JSONResponse({"success": False, "error": "unauthorized"}, status_code=401)
    if payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{ANIME_API_URL}/anime/{anime_id}",
            timeout=10.0
        )

        if response.status_code == 204:
            return RedirectResponse(url="/admin/anime", status_code=303)

    return RedirectResponse(url="/admin/anime?error=Failed+to+delete+anime", status_code=303)


async def get_news_by_id(news_id: int) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/news/{news_id}", timeout=10.0)
        if response.status_code == 200:
            return response.json()
    return None


@router.get("/news", response_class=HTMLResponse)
@require_auth
async def admin_news_list(
        request: Request,
        page: int = 1,
        size: int = 20,
        payload: dict = None
):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ANIME_API_URL}/news/",
            params={"page": page, "size": size},
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()
            news_list = data.get("items", [])
            total = data.get("total", 0)
            total_pages = data.get("pages", 0)
        else:
            news_list = []
            total = 0
            total_pages = 0

    return templates.TemplateResponse("admin_news_list.html", {
        "request": request,
        "is_authorized": True,
        "is_admin": True,
        "news_list": news_list,
        "total_pages": total_pages,
        "current_page": page,
        "title": "Manage News"
    })


@router.get("/news/create", response_class=HTMLResponse)
@require_auth
async def admin_news_create_form(
        request: Request,
        payload: dict = None
):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    return templates.TemplateResponse("admin_news_form.html", {
        "request": request,
        "is_authorized": True,
        "is_admin": True,
        "title": "Create News",
        "news": None
    })


@router.post("/news/create", response_class=HTMLResponse)
@require_auth
async def admin_news_create(
        request: Request,
        title: str = Form(...),
        slug: str = Form(...),
        preview_text: str = Form(...),
        full_content: str = Form(...),
        is_published: str = Form("false"),
        preview_image: Optional[UploadFile] = File(None),
        full_image: Optional[UploadFile] = File(None),
        payload: dict = None
):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    # Upload images to S3
    preview_image_url = None
    full_image_url = None

    if preview_image and preview_image.filename:
        try:
            result = await upload_image(upload_type="news", file=preview_image)
            preview_image_url = result["url"]
        except Exception as e:
            return RedirectResponse(url="/admin/news/create?error=Failed+to+upload+preview+image", status_code=303)

    if full_image and full_image.filename:
        try:
            result = await upload_image(upload_type="news", file=full_image)
            full_image_url = result["url"]
        except Exception as e:
            return RedirectResponse(url="/admin/news/create?error=Failed+to+upload+full+image", status_code=303)

    data = {
        "title": title,
        "slug": slug,
        "preview_text": preview_text,
        "full_content": full_content,
        "is_published": is_published.lower() == "true",
        "preview_image_url": preview_image_url,
        "full_image_url": full_image_url
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ANIME_API_URL}/news/",
            headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"},
            json=data,
            timeout=10.0
        )
        print(response.status_code)
        if response.status_code == 201:
            return RedirectResponse(url="/admin/news", status_code=303)

    return RedirectResponse(url="/admin/news/create?error=Failed+to+create+news", status_code=303)


@router.get("/news/{news_id}/edit", response_class=HTMLResponse)
@require_auth
async def admin_news_edit_form(
        request: Request,
        news_id: int,
        payload: dict = None
):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    news = await get_news_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return templates.TemplateResponse("admin_news_form.html", {
        "request": request,
        "is_authorized": True,
        "is_admin": True,
        "title": f"Edit News — {news.get('title', 'Untitled')}",
        "news": news
    })


@router.post("/news/{news_id}/edit", response_class=HTMLResponse)
@require_auth
async def admin_news_edit(
        request: Request,
        news_id: int,
        title: Optional[str] = Form(None),
        slug: Optional[str] = Form(None),
        preview_text: Optional[str] = Form(None),
        full_content: Optional[str] = Form(None),
        is_published: Optional[str] = Form(None),
        preview_image_url: Optional[UploadFile] = File(None),
        full_image_url: Optional[UploadFile] = File(None),
        payload: dict = None
):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    data = {
        "title": title,
        "slug": slug,
        "preview_text": preview_text,
        "full_content": full_content,
    }

    if is_published is not None:
        data["is_published"] = is_published.lower() == "true"

    # Upload new images if provided
    if preview_image_url and preview_image_url.filename:
        try:
            result = await upload_image(upload_type="news", file=preview_image_url)
            data["preview_image_url"] = result["url"]
        except Exception as e:
            return RedirectResponse(url=f"/admin/news/{news_id}/edit?error=Failed+to+upload+preview+image",
                                    status_code=303)

    if full_image_url and full_image_url.filename:
        try:
            result = await upload_image(upload_type="news", file=full_image_url)
            data["full_image_url"] = result["url"]
        except Exception as e:
            return RedirectResponse(url=f"/admin/news/{news_id}/edit?error=Failed+to+upload+full+image",
                                    status_code=303)

    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{ANIME_API_URL}/news/{news_id}",
            headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"},
            json=data,
            timeout=10.0
        )
        print(response.status_code)
        if response.status_code == 200:
            return RedirectResponse(url="/admin/news", status_code=303)

    return RedirectResponse(url=f"/admin/news/{news_id}/edit?error=Failed+to+update+news", status_code=303)


@router.post("/news/{news_id}/delete", response_class=HTMLResponse)
@require_auth
async def admin_news_delete(
        request: Request,
        news_id: int,
        payload: dict = None
):
    if not payload or payload.get(RoleKey) not in (RoleADMIN, RoleMODER):
        return JSONResponse({"success": False, "error": "forbidden"}, status_code=403)

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{ANIME_API_URL}/news/{news_id}",
            headers={"Authorization": f"Bearer {request.cookies.get('access_token')}"},
            timeout=10.0
        )

        if response.status_code == 204:
            return RedirectResponse(url="/admin/news", status_code=303)

    return RedirectResponse(url="/admin/news?error=Failed+to+delete+news", status_code=303)