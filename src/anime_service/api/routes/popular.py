from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import List
from src.anime_service.repositories.popular_anime_repo import PopularAnimeRepository
from src.anime_service.repositories.anime_repo import AnimeRepository
from src.anime_service.schemas.popular_anime import (
    PopularAnimeCreate, PopularAnimeUpdate,
    PopularAnimeResponse, PopularAnimeWithDetailsResponse
)
from src.anime_service.api.deps import require_moder_or_admin

router = APIRouter(prefix="/popular-anime", tags=["popular-anime"])


@router.get("/", response_model=List[PopularAnimeWithDetailsResponse])
async def get_popular_anime(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        with_full_details: bool = Query(False, description="Получить с жанрами, темами и студиями")
):
    """Получить список популярных аниме (публичный)"""
    offset = (page - 1) * size

    if with_full_details:
        popular_items = PopularAnimeRepository.get_popular_with_full_details(limit=size, offset=offset)
        # Трансформируем в нужный формат
        result = []
        for item in popular_items:
            anime_data = {
                'id': item['anime_id'],
                'title_english': item['title_english'],
                'image_webp_large_url': item['image_webp_large_url'],
                'trailer_url': item.get('trailer_url'),
                'type': item['type'],
                'episodes': item['episodes'],
                'duration': item['duration'],
                'rating': item['rating'],
                'synopsis': item['synopsis'],
                'background': item.get('background'),
                'year': item['year'],
                'genres': item['genres'],
                'themes': item['themes'],
                'demographics': item['demographics'],
                'studios': item['studios']
            }
            result.append({
                'id': item['popular_id'],
                'anime': anime_data,
                'large_poster_url': item['large_poster_url']
            })
        return result
    else:
        popular_items = PopularAnimeRepository.get_popular_with_anime_details(limit=size, offset=offset)
        result = []
        for item in popular_items:
            anime_data = {
                'id': item['anime_id'],
                'title_english': item['title_english'],
                'image_webp_large_url': item['image_webp_large_url'],
                'type': item['type'],
                'episodes': item['episodes'],
                'duration': item['duration'],
                'rating': item['rating'],
                'synopsis': item['synopsis'],
                'year': item['year']
            }
            result.append({
                'id': item['popular_id'],
                'anime': anime_data,
                'large_poster_url': item['large_poster_url']
            })
        return result


@router.get("/{popular_id}", response_model=PopularAnimeWithDetailsResponse)
async def get_popular_anime_by_id(popular_id: int):
    """Получить популярное аниме по ID записи (публичный)"""
    popular = PopularAnimeRepository.get_by_id(popular_id)
    if not popular:
        raise HTTPException(status_code=404, detail="Popular anime entry not found")

    anime = AnimeRepository.get_details(popular['anime_id'])
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    return {
        'id': popular['id'],
        'anime': anime,
        'large_poster_url': popular['large_poster_url']
    }


@router.get("/by-anime/{anime_id}", response_model=PopularAnimeWithDetailsResponse)
async def get_popular_by_anime_id(anime_id: int):
    """Получить запись популярного аниме по ID аниме (публичный)"""
    popular = PopularAnimeRepository.get_by_anime_id(anime_id)
    if not popular:
        raise HTTPException(status_code=404, detail="Anime not found in popular list")

    anime = AnimeRepository.get_details(anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    return {
        'id': popular['id'],
        'anime': anime,
        'large_poster_url': popular['large_poster_url']
    }


# Защищенные эндпоинты (только модеры и админы)
@router.post("/", response_model=PopularAnimeResponse, status_code=status.HTTP_201_CREATED)
async def add_to_popular(
        popular_anime: PopularAnimeCreate,
        user: dict = Depends(require_moder_or_admin)
):
    """Добавить аниме в популярные (только модеры и админы)"""
    # Проверяем, существует ли аниме
    anime = AnimeRepository.get_by_id(popular_anime.anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")

    # Проверяем, не добавлено ли уже
    existing = PopularAnimeRepository.get_by_anime_id(popular_anime.anime_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Anime with ID {popular_anime.anime_id} is already in popular list"
        )

    popular_id = PopularAnimeRepository.create(popular_anime.model_dump())
    created = PopularAnimeRepository.get_by_id(popular_id)

    return PopularAnimeResponse(**created)


@router.put("/{popular_id}", response_model=PopularAnimeResponse)
async def update_popular_anime(
        popular_id: int,
        popular_anime: PopularAnimeUpdate,
        user: dict = Depends(require_moder_or_admin)
):
    """Обновить запись популярного аниме (только модеры и админы)"""
    existing = PopularAnimeRepository.get_by_id(popular_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Popular anime entry not found")

    updated = PopularAnimeRepository.update(popular_id, popular_anime.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=400, detail="Update failed")

    result = PopularAnimeRepository.get_by_id(popular_id)
    return PopularAnimeResponse(**result)


@router.delete("/{popular_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_popular(
        popular_id: int,
        user: dict = Depends(require_moder_or_admin)
):
    """Удалить аниме из популярных (только модеры и админы)"""
    deleted = PopularAnimeRepository.delete(popular_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Popular anime entry not found")


@router.delete("/by-anime/{anime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_popular_by_anime_id(
        anime_id: int,
        user: dict = Depends(require_moder_or_admin)
):
    """Удалить аниме из популярных по ID аниме (только модеры и админы)"""
    deleted = PopularAnimeRepository.delete_by_anime_id(anime_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Anime not found in popular list")
