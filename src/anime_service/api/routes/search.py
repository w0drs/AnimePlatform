from fastapi import APIRouter, Query, Path
from src.anime_service.repositories.anime_repo import AnimeRepository

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
async def search_anime(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=50, description="Лимит результатов")
):
    """Поиск аниме по названию или синопсису"""
    results = AnimeRepository.search(q, limit)
    return {
        "query": q,
        "total": len(results),
        "results": results
    }

@router.get("/year/{year}")
async def filter_by_year(
    year: int = Path(..., description="Год выпуска"),
    limit: int = Query(100, ge=1, le=200)
):
    """Фильтрация аниме по году"""
    results = AnimeRepository.filter_by_year(year, limit)
    return {
        "year": year,
        "total": len(results),
        "results": results
    }