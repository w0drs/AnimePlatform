from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
import httpx
from typing import Optional
from fastapi.responses import HTMLResponse
import urllib.parse

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
        type: Optional[str] = None,
        rating: Optional[str] = None,
        genre: Optional[str] = None,
        theme: Optional[str] = None,
        demographic: Optional[str] = None,
        studio: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        error: Optional[str] = None
):
    """Страница каталога аниме"""

    # Проверка авторизации
    payload, needs_refresh = await jwt_service.verify(request)
    is_authorized, is_admin = False, False

    if not needs_refresh:
        is_authorized = True
        is_admin = payload.get("role") in ["admin", "moder"]

    # Обработка пустых строк в параметрах
    def clean_param(value):
        if value == "" or value is None:
            return None
        return value

    # Преобразуем год в int если он есть и не пустой
    year_int = None
    if year and year != "":
        try:
            year_int = int(year)
        except ValueError:
            year_int = None

    # Запрос к API аниме-сервиса
    anime_list = []
    total = 0

    async with httpx.AsyncClient() as client:
        try:
            params = {
                "page": page,
                "size": size
            }

            if year_int:
                params["year"] = year_int
            if clean_param(type):
                params["type"] = type
            if clean_param(rating):
                params["rating"] = rating
            if clean_param(genre):
                params["genre"] = genre
            if clean_param(theme):
                params["theme"] = theme
            if clean_param(demographic):
                params["demographic"] = demographic
            if clean_param(studio):
                params["studio"] = studio
            if clean_param(search):
                params["search"] = search

            response = await client.get(
                "http://localhost:8001/anime/filter",
                params=params,
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                anime_list = data.get("items", [])
                total = data.get("total", 0)
            else:
                error = f"API error: {response.status_code}"

        except httpx.TimeoutException:
            error = "Request timeout"
        except httpx.ConnectError:
            error = "Cannot connect to anime service"
        except Exception as e:
            error = f"Error: {str(e)}"

    # Корректный расчет количества страниц
    if total <= 0:
        total_pages = 0
    elif total <= size:
        total_pages = 1
    else:
        total_pages = (total + size - 1) // size

    # Функция для построения URL с правильным кодированием
    def build_pagination_url(page_num: int) -> str:
        """Строит URL для пагинации с сохранением всех фильтров"""
        url_params = {}

        if year:
            url_params["year"] = year
        if type:
            url_params["type"] = type
        if rating:
            url_params["rating"] = rating
        if genre:
            url_params["genre"] = genre
        if theme:
            url_params["theme"] = theme
        if demographic:
            url_params["demographic"] = demographic
        if studio:
            url_params["studio"] = studio
        if search:
            url_params["search"] = search

        url_params["page"] = page_num
        url_params["size"] = size

        # Правильное кодирование параметров
        encoded_params = []
        for key, value in url_params.items():
            encoded_value = urllib.parse.quote(str(value), safe='')
            encoded_params.append(f"{key}={encoded_value}")

        return f"/catalog?{'&'.join(encoded_params)}"

    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "active_page": "catalog",
        "is_authorized": is_authorized,
        "is_admin": is_admin,
        "anime_list": anime_list,
        "total_count": total,
        "total_pages": total_pages,
        "current_page": page,
        "size": size,
        "current_year": year,
        "current_type": type,
        "current_rating": rating,
        "current_genre": genre,
        "current_theme": theme,
        "current_demographic": demographic,
        "current_studio": studio,
        "current_search": search,
        "build_pagination_url": build_pagination_url,
        "error": error
    })
