from fastapi import APIRouter, HTTPException, Query, status, Depends
from src.anime_service.repositories.news_repo import NewsRepository
from src.anime_service.schemas.news import (
    NewsCreate, NewsPreviewUpdate, NewsContentUpdate,
    NewsPreviewResponse, NewsDetailResponse, NewsListResponse
)
from src.anime_service.api.deps import require_moder_or_admin

router = APIRouter(prefix="/news", tags=["news"])


# Публичные эндпоинты (доступны всем)
@router.get("/", response_model=NewsListResponse)
async def get_all_news(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        include_unpublished: bool = Query(False)
):
    """Получить список всех новостей (публичный)"""
    offset = (page - 1) * size
    items = NewsRepository.get_all(limit=size, offset=offset, only_published=not include_unpublished)
    total = NewsRepository.count(only_published=not include_unpublished)

    return NewsListResponse(
        items=[NewsPreviewResponse(**item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{news_id}", response_model=NewsDetailResponse)
async def get_news_by_id(news_id: int):
    """Получить новость по ID (публичный)"""
    news = NewsRepository.get_by_id(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return NewsDetailResponse(**news)


@router.get("/slug/{slug}", response_model=NewsDetailResponse)
async def get_news_by_slug(slug: str):
    """Получить новость по slug (публичный)"""
    news = NewsRepository.get_by_slug(slug)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return NewsDetailResponse(**news)


# Защищенные эндпоинты (только модеры и админы)
@router.post("/", response_model=NewsDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
        news: NewsCreate,
        user: dict = Depends(require_moder_or_admin)  # ← проверка прав
):
    """Создать новую новость (только модеры и админы)"""
    news_id = NewsRepository.create(news.model_dump())
    created = NewsRepository.get_by_id(news_id)
    return NewsDetailResponse(**created)


@router.put("/{news_id}", response_model=NewsDetailResponse)
async def update_news(
        news_id: int,
        preview_data: NewsPreviewUpdate,
        content_data: NewsContentUpdate,
        user: dict = Depends(require_moder_or_admin)  # ← проверка прав
):
    """Обновить новость (только модеры и админы)"""
    NewsRepository.update_preview(news_id, preview_data.model_dump(exclude_none=True))
    NewsRepository.update_content(news_id, content_data.model_dump(exclude_none=True))

    updated = NewsRepository.get_by_id(news_id)
    if not updated:
        raise HTTPException(status_code=404, detail="News not found")
    return NewsDetailResponse(**updated)


@router.patch("/{news_id}/publish", response_model=NewsPreviewResponse)
async def toggle_publish(
        news_id: int,
        is_published: bool = Query(...),
        user: dict = Depends(require_moder_or_admin)  # ← проверка прав
):
    """Переключить статус публикации (только модеры и админы)"""
    updated = NewsRepository.toggle_publish(news_id, is_published)
    if not updated:
        raise HTTPException(status_code=404, detail="News not found")

    news = NewsRepository.get_by_id(news_id)
    return NewsPreviewResponse(**news)


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
        news_id: int,
        user: dict = Depends(require_moder_or_admin)  # ← проверка прав
):
    """Удалить новость (только модеры и админы)"""
    deleted = NewsRepository.delete(news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
