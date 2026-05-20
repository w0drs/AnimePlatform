from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Optional
from pathlib import Path

from src.frontend.services.jwt_service import jwt_service
from src.frontend.services.auth_service import auth_service
from src.frontend.schemas import users

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

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

@router.get("/catalog", response_class=HTMLResponse)
def catalog(
        request: Request,

        error: Optional[str] = None
):
    """
    GET /catalog - Показывает HTML форму каталога аниме
    """

    # заглушка
    return templates.TemplateResponse("main.html", {
        "request": request,
        "active_page": "home",
        "recommended": [],  # список словарей с полями title, year, rating, image
        "popular": [],
        "is_authorized": "true",
        "is_admin": "true",
    }
)