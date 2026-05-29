from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import Optional, List
from src.anime_service.repositories.anime_repo import AnimeRepository
from src.anime_service.schemas.anime import (
    AnimeCreate, AnimeUpdate, AnimeResponse,
    AnimeDetailResponse, AnimeListResponse
)
from src.anime_service.api.deps import require_moder_or_admin

router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("/filter", response_model=AnimeListResponse)
async def filter_anime(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    year: Optional[int] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    type: Optional[str] = Query(None, alias="anime_type"),
    rating: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    theme: Optional[str] = Query(None),
    demographic: Optional[str] = Query(None),
    studio: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Фильтрация аниме с пагинацией"""
    offset = (page - 1) * size

    # Исправлено: filter_anime вместо filter
    items, total = AnimeRepository.filter_anime(
        limit=size,
        offset=offset,
        year=year,
        year_from=year_from,
        year_to=year_to,
        anime_type=type,
        rating=rating,
        genre=genre,
        theme=theme,
        demographic=demographic,
        studio=studio,
        search=search
    )

    return AnimeListResponse(
        items=[AnimeDetailResponse(**item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0
    )


@router.get("/by-ids", response_model=List[AnimeDetailResponse])
async def get_anime_by_ids(
    ids: str = Query(..., description="ID через запятую, например: 1,2,3")
):
    """Получить аниме по списку ID с жанрами и темами"""
    try:
        ids_list = [int(id_str.strip()) for id_str in ids.split(',') if id_str.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if not ids_list:
        raise HTTPException(status_code=400, detail="IDs list cannot be empty")

    unique_ids = list(set(ids_list))
    anime_list = AnimeRepository.get_by_ids(unique_ids)

    if not anime_list:
        raise HTTPException(status_code=404, detail="No anime found")

    result = []
    for anime in anime_list:
        anime_id = anime['id']
        anime['genres'] = AnimeRepository.get_genres_by_anime_id(anime_id)
        anime['themes'] = AnimeRepository.get_themes_by_anime_id(anime_id)
        anime['demographics'] = AnimeRepository.get_demographics_by_anime_id(anime_id)
        anime['studios'] = AnimeRepository.get_studios_by_anime_id(anime_id)
        result.append(AnimeDetailResponse(**anime))

    return result


@router.get("/{anime_id}", response_model=AnimeDetailResponse)
async def get_anime(anime_id: int):
    """Получить аниме по ID"""
    anime = AnimeRepository.get_details(anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return AnimeDetailResponse(**anime)


@router.get("/search", response_model=List[AnimeResponse])
async def search_anime(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=50, description="Лимит результатов")
):
    """Быстрый поиск аниме по названию"""
    results = AnimeRepository.search(q, limit)
    return [AnimeResponse(**item) for item in results]


@router.post("/", response_model=AnimeResponse, status_code=status.HTTP_201_CREATED)
async def create_anime(
    anime: AnimeCreate,
    user: dict = Depends(require_moder_or_admin)
):
    """Создать аниме (только модеры и админы)"""
    anime_id = AnimeRepository.create(anime.model_dump(exclude_none=True))
    created = AnimeRepository.get_by_id(anime_id)
    return AnimeResponse(**created)


@router.put("/{anime_id}", response_model=AnimeResponse)
async def update_anime(
    anime_id: int,
    anime: AnimeUpdate,
    user: dict = Depends(require_moder_or_admin)
):
    """Обновить аниме (только модеры и админы)"""
    updated = AnimeRepository.update(anime_id, anime.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Anime not found")

    result = AnimeRepository.get_by_id(anime_id)
    return AnimeResponse(**result)


@router.delete("/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_anime(
    anime_id: int,
    user: dict = Depends(require_moder_or_admin)
):
    """Удалить аниме (только модеры и админы)"""
    deleted = AnimeRepository.delete(anime_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Anime not found")