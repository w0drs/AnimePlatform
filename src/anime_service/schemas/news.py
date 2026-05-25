from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Базовые схемы
class NewsPreviewBase(BaseModel):
    title: str
    slug: str
    preview_text: str
    preview_image_url: Optional[str] = None
    is_published: bool = True


class NewsContentBase(BaseModel):
    full_content: str
    full_image_url: Optional[str] = None


# Создание новости
class NewsCreate(NewsPreviewBase):
    full_content: str
    full_image_url: Optional[str] = None


# Обновление новости
class NewsPreviewUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    preview_text: Optional[str] = None
    preview_image_url: Optional[str] = None
    is_published: Optional[bool] = None


class NewsContentUpdate(BaseModel):
    full_content: Optional[str] = None
    full_image_url: Optional[str] = None


# Ответ с превью (для списка)
class NewsPreviewResponse(NewsPreviewBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Ответ с полным содержанием (для детального просмотра)
class NewsDetailResponse(NewsPreviewResponse):
    full_content: str
    full_image_url: Optional[str] = None


# Список с пагинацией
class NewsListResponse(BaseModel):
    items: List[NewsPreviewResponse]
    total: int
    page: int
    size: int
    pages: int
