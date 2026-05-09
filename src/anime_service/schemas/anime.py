from pydantic import BaseModel
from typing import Optional, List


# Базовые схемы
class AnimeBase(BaseModel):
    title_english: Optional[str] = None
    image_webp_large_url: Optional[str] = None
    trailer_url: Optional[str] = None
    type: Optional[str] = None
    episodes: Optional[int] = None
    duration: Optional[str] = None
    rating: Optional[str] = None
    synopsis: Optional[str] = None
    background: Optional[str] = None
    year: Optional[int] = None


# Создание аниме
class AnimeCreate(AnimeBase):
    title_english: str  # обязательное поле при создании


# Обновление аниме
class AnimeUpdate(BaseModel):
    title_english: Optional[str] = None
    image_webp_large_url: Optional[str] = None
    trailer_url: Optional[str] = None
    type: Optional[str] = None
    episodes: Optional[int] = None
    duration: Optional[str] = None
    rating: Optional[str] = None
    synopsis: Optional[str] = None
    background: Optional[str] = None
    year: Optional[int] = None


# Ответ с аниме (включая ID)
class AnimeResponse(AnimeBase):
    id: int

    class Config:
        from_attributes = True


# Аниме с жанрами и темами (для детального просмотра)
class AnimeDetailResponse(AnimeResponse):
    genres: List[str] = []
    themes: List[str] = []
    demographics: List[str] = []
    studios: List[str] = []


# Список с пагинацией
class AnimeListResponse(BaseModel):
    items: List[AnimeResponse]
    total: int
    page: int
    size: int
    pages: int