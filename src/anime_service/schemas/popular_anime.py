from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PopularAnimeBase(BaseModel):
    anime_id: int
    large_poster_url: str


class PopularAnimeCreate(PopularAnimeBase):
    pass


class PopularAnimeUpdate(BaseModel):
    large_poster_url: Optional[str] = None


class PopularAnimeResponse(BaseModel):
    id: int
    anime_id: int
    large_poster_url: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PopularAnimeWithDetailsResponse(BaseModel):
    id: int
    anime: dict
    large_poster_url: str
