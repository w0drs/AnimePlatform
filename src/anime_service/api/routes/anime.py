from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import Optional, List
from src.anime_service.repositories.anime_repo import AnimeRepository
from src.anime_service.schemas.anime import (
    AnimeCreate, AnimeUpdate, AnimeResponse,
    AnimeDetailResponse, AnimeListResponse
)
from src.anime_service.api.deps import require_moder_or_admin, get_current_user_optional

router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("/", response_model=AnimeListResponse)
async def get_all_anime(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        user: Optional[dict] = Depends(get_current_user_optional)
):
    """Получить список всех аниме с жанрами, темами, студиями (публичный)"""
    offset = (page - 1) * size
    items = AnimeRepository.get_all_with_relations(limit=size, offset=offset)
    total = AnimeRepository.count()

    return AnimeListResponse(
        items=[AnimeDetailResponse(**item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/by-ids", response_model=List[AnimeDetailResponse])
async def get_anime_by_ids(
        ids: str = Query(..., description="ID аниме через запятую, например: 1,2,3")
):
    """Получить аниме по списку ID с жанрами, темами, студиями (публичный)"""
    try:
        ids_list = [int(id_str.strip()) for id_str in ids.split(',') if id_str.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format. IDs must be integers")

    if not ids_list:
        raise HTTPException(status_code=400, detail="IDs list cannot be empty")

    unique_ids = list(set(ids_list))
    anime_list = AnimeRepository.get_by_ids(unique_ids)

    if not anime_list:
        raise HTTPException(status_code=404, detail="No anime found for provided IDs")

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
    """Получить аниме по ID с жанрами, темами, студиями (публичный)"""
    anime = AnimeRepository.get_details(anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return AnimeDetailResponse(**anime)


@router.get("/list/all", response_model=AnimeListResponse)
async def get_all_anime_filtered(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        year: Optional[int] = Query(None),
        type: Optional[str] = Query(None),
        min_rating: Optional[str] = Query(None)
):
    """Получить список аниме с фильтрацией, жанрами, темами, студиями (публичный)"""
    offset = (page - 1) * size
    items = AnimeRepository.get_all_with_filters(
        limit=size, offset=offset, year=year, type=type, min_rating=min_rating
    )

    for anime in items:
        anime_id = anime['id']
        anime['genres'] = AnimeRepository.get_genres_by_anime_id(anime_id)
        anime['themes'] = AnimeRepository.get_themes_by_anime_id(anime_id)
        anime['demographics'] = AnimeRepository.get_demographics_by_anime_id(anime_id)
        anime['studios'] = AnimeRepository.get_studios_by_anime_id(anime_id)

    total = AnimeRepository.count()

    return AnimeListResponse(
        items=[AnimeDetailResponse(**item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.post("/", response_model=AnimeResponse, status_code=status.HTTP_201_CREATED)
async def create_anime(
        anime: AnimeCreate,
        user: dict = Depends(require_moder_or_admin)
):
    """Создать новое аниме (только модеры и админы)"""
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
