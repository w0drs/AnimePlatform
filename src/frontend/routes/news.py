from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/news", response_class=HTMLResponse)
def news(
        request: Request,
        error: Optional[str] = None
):
    """
    GET /news - Показывает HTML форму страницы новостей
    """

    # заглушка
    return templates.TemplateResponse("main.html", {
        "request": request,
        "active_page": "home",
        "recommended": [...],  # список словарей с полями title, year, rating, image
        "popular": [...],
        "is_authorized": "true",
        "is_admin": "true",
    }
)