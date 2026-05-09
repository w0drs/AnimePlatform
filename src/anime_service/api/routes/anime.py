from fastapi import APIRouter, HTTPException, Query, status
from src.anime_service.repositories.anime_repo import AnimeRepository
from src.anime_service.schemas.anime import (
    AnimeCreate, AnimeUpdate, AnimeResponse,
    AnimeDetailResponse, AnimeListResponse
)

router = APIRouter(prefix="/anime", tags=["anime"])


@router.get("/", response_model=AnimeListResponse)
async def get_all_anime(
        page: int = Query(1, ge=1, description="Номер страницы"),
        size: int = Query(20, ge=1, le=100, description="Размер страницы")
):
    """Получить список всех аниме с пагинацией"""
    offset = (page - 1) * size
    items = AnimeRepository.get_all(limit=size, offset=offset)
    total = AnimeRepository.count()

    return AnimeListResponse(
        items=[AnimeResponse(**item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{anime_id}", response_model=AnimeDetailResponse)
async def get_anime(anime_id: int):
    """Получить аниме по ID с жанрами и темами"""
    anime = AnimeRepository.get_details(anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return AnimeDetailResponse(**anime)


@router.post("/", response_model=AnimeResponse, status_code=status.HTTP_201_CREATED)
async def create_anime(anime: AnimeCreate):
    """Создать новое аниме"""
    anime_id = AnimeRepository.create(anime.model_dump(exclude_none=True))
    created = AnimeRepository.get_by_id(anime_id)
    return AnimeResponse(**created)


@router.put("/{anime_id}", response_model=AnimeResponse)
async def update_anime(anime_id: int, anime: AnimeUpdate):
    """Обновить аниме"""
    updated = AnimeRepository.update(anime_id, anime.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Anime not found")

    result = AnimeRepository.get_by_id(anime_id)
    return AnimeResponse(**result)


@router.delete("/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_anime(anime_id: int):
    """Удалить аниме"""
    deleted = AnimeRepository.delete(anime_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Anime not found")