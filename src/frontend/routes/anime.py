from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
from pathlib import Path

from src.frontend.services.jwt_service import jwt_service
from src.frontend.schemas import users
from src.frontend.services.anime_service import anime_service


BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.globals.update(max=max, min=min)

@router.get("/main", response_class=HTMLResponse)
async def main(
        request: Request,
        error: Optional[str] = None
):
    """
    GET /main - Показывает HTML форму главной страницы
    """
    payload, needs_refresh = await jwt_service.verify(request)
    is_authorized, is_admin = False, False
    if not needs_refresh:
        is_authorized = True
        is_admin = payload["role"] == users.RoleADMIN or payload["role"] == users.RoleMODER

    return templates.TemplateResponse("main.html", {
        "request": request,
        "active_page": "home",

        "is_authorized": is_authorized,
        "is_admin": is_admin,

        "recommended": [...],  # список словарей с полями title, year, rating, image
        "popular": [...],

    }
)


@router.get("/anime/{anime_id}", response_class=HTMLResponse)
async def anime_page(
        request: Request,
        anime_id: int,
        page: int = 1,
        error: Optional[str] = None
):
    """
    GET /anime/{anime_id} - Страница детального просмотра аниме
    """
    payload, needs_refresh = await jwt_service.verify(request)
    is_authorized, is_admin = False, False
    if not needs_refresh:
        is_authorized = True
        is_admin = payload["role"] == users.RoleADMIN or payload["role"] == users.RoleMODER
    # получаем аниме

    data = await anime_service.get_anime_page_data(anime_id, page=page, access_token=request.cookies.get("access_token"))
    anime = data["anime"]
    is_favorite = data["is_favorite"]

    # Данные аниме
    anime_data = {
        "id": anime_id,
        "title_english": anime["title_english"],
        "type": anime["type"],
        "episodes": anime["episodes"],
        "duration": anime["duration"],
        "rating": anime["rating"],
        "year": anime["year"],
        "synopsis": anime["synopsis"],
        "background": None,
        "trailer_url": anime["trailer_url"],
        "image_webp_large_url": anime["image_webp_large_url"]
    }
    # Жанры
    genres = anime['genres']
    # Студии
    studios = anime['studios']
    # Похожие аниме
    similar_anime = data["recommendations"]
    # Комментарии
    comments = data["comments"]

    total_pages = 1
    current_page = 1

    limit = 10
    return templates.TemplateResponse("anime_detail.html", {
        "request": request,
        "active_page": "anime",
        "is_authorized": is_authorized,
        "is_admin": is_admin,
        "user_avatar": payload.get("icon_url", None),

        # Данные аниме
        "anime": anime_data,
        "genres": genres,
        "studios": studios,

        # Похожие аниме
        "similar_anime": similar_anime,

        # Комментарии
        "comments": comments,
        "total_pages": total_pages,
        "current_page": current_page,

        #Есть ли в избранном
        "is_favorite": is_favorite,

        # Для пагинации htmx
        "anime_id": anime_id,
        "page": 1,
        "has_next": len(comments) == limit,
        "has_prev": False,
    })

@router.get("/catalog", response_class=HTMLResponse, name="catalog")
async def catalog(
        request: Request,
        year: Optional[str] = None,
        genre: Optional[str] = None,
        rating: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        error: Optional[str] = None
):
    """Страница каталога аниме"""
    # Проверка авторизации
    payload, needs_refresh = await jwt_service.verify(request)
    is_authorized, is_admin = False, False
    # Простая проверка токена
    if not needs_refresh:
        is_authorized = True
        is_admin = payload["role"] == users.RoleADMIN or payload["role"] == users.RoleMODER

    # Заглушка для фильтров
    filters = {
        "year": year,
        "genre": genre,
        "rating": rating,
        "status": status,
        "search": search
    }

    # Заглушка для списка аниме (замените на реальные данные из БД)
    anime_list = [
        {"id": 1, "title_english": "Атака Титанов", "rating": "9.2", "image_webp_large_url": ""},
        {"id": 2, "title_english": "Магическая битва", "rating": "8.9", "image_webp_large_url": ""},
        {"id": 3, "title_english": "One Piece", "rating": "9.1", "image_webp_large_url": ""},
        {"id": 4, "title_english": "Тетрадь смерти", "rating": "9.0", "image_webp_large_url": ""},
        {"id": 5, "title_english": "Человек-бензопила", "rating": "8.6", "image_webp_large_url": ""},
        {"id": 6, "title_english": "Spy×Family", "rating": "8.8", "image_webp_large_url": ""},
    ]

    # Заглушка для жанров (замените на реальные данные из БД)
    all_genres = [
        {"id": 1, "name": "Экшен"},
        {"id": 2, "name": "Комедия"},
        {"id": 3, "name": "Драма"},
        {"id": 4, "name": "Романтика"},
        {"id": 5, "name": "Фэнтези"},
        {"id": 6, "name": "Научная фантастика"},
        {"id": 7, "name": "Ужасы"},
    ]

    total_count = len(anime_list)
    total_pages = 1
    current_page = page

    # Функция для обновления параметров запроса
    def update_query(**kwargs):
        params = {
            "year": year,
            "genre": genre,
            "rating": rating,
            "status": status,
            "search": search,
            "page": page
        }
        params.update(kwargs)
        # Убираем пустые значения
        params = {k: v for k, v in params.items() if v}
        return "&".join([f"{k}={v}" for k, v in params.items()])

    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "active_page": "catalog",
        "is_authorized": is_authorized,
        "is_admin": is_admin,
        "anime_list": anime_list,
        "all_genres": all_genres,
        "filters": filters,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": current_page,
        "update_query": update_query,
    })
