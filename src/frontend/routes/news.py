from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional
from pathlib import Path
from src.frontend.config.settings import settings

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# API бэкенда
ANIME_API_URL = settings.news_service


@router.get("/news", response_class=HTMLResponse, name="news")
async def news_page(
        request: Request,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=50),
        error: Optional[str] = None
):
    """Страница новостей с реальными данными из API"""

    offset = (page - 1) * size

    async with httpx.AsyncClient() as client:
        try:
            # Получаем новости из API бэкенда (только опубликованные)
            response = await client.get(
                f"{ANIME_API_URL}/news/",
                params={"page": page, "size": size, "include_unpublished": False},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                news_list = data.get("items", [])
                total = data.get("total", 0)
                total_pages = data.get("pages", 0)
            else:
                error = f"API error: {response.status_code}"
                news_list = []
                total = 0
                total_pages = 0

        except httpx.TimeoutException:
            error = "Request timeout"
            news_list = []
            total = 0
            total_pages = 0
        except httpx.ConnectError:
            error = "Cannot connect to anime service"
            news_list = []
            total = 0
            total_pages = 0
        except Exception as e:
            error = f"Error: {str(e)}"
            news_list = []
            total = 0
            total_pages = 0

    return templates.TemplateResponse("news.html", {
        "request": request,
        "active_page": "news",
        "is_authorized": False,
        "is_admin": False,
        "news_list": news_list,
        "total_count": total,
        "total_pages": total_pages,
        "current_page": page,
        "error": error
    })


@router.get("/news/{news_id}", response_class=HTMLResponse, name="news_detail")
async def news_detail_page(
        request: Request,
        news_id: int,
        error: Optional[str] = None
):
    """Страница отдельной новости с реальными данными из API"""

    async with httpx.AsyncClient() as client:
        try:
            # Получаем новость из API бэкенда
            response = await client.get(
                f"{ANIME_API_URL}/news/{news_id}",
                timeout=10.0
            )

            if response.status_code == 200:
                news_data = response.json()
            else:
                raise HTTPException(status_code=404, detail="News not found")

        except httpx.TimeoutException:
            error = "Request timeout"
            raise HTTPException(status_code=500, detail="Request timeout")
        except httpx.ConnectError:
            error = "Cannot connect to anime service"
            raise HTTPException(status_code=500, detail="Cannot connect to anime service")
        except Exception as e:
            error = str(e)
            raise HTTPException(status_code=404, detail="News not found")

    return templates.TemplateResponse("news_detail.html", {
        "request": request,
        "active_page": "news",
        "is_authorized": False,
        "is_admin": False,
        "news": news_data,
        "error": error
    })