import asyncio
import httpx

from src.frontend.config.settings import settings


class MainService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

    async def get_recommendations(self, user_id: str) -> list:
        if not user_id:
            return []
        try:
            response = await self.client.get(
                f"{settings.anime_service}/recommend/collaborative/{user_id}",
            )
        except httpx.RequestError:
            return []
        if response.status_code != 200:
            return []
        return response.json().get("recommendations", [])

    async def get_popular(self, size: int = 5) -> list:
        try:
            response = await self.client.get(
                f"{settings.anime_service}/popular-anime/",
                params={"page": 1, "size": size, "with_full_details": False},
            )
        except httpx.RequestError:
            return []
        if response.status_code != 200:
            return []
        return response.json()

    async def get_news(self, size: int = 5) -> list:
        try:
            response = await self.client.get(
                f"{settings.anime_service}/news/",
                params={"page": 1, "size": size, "include_unpublished": False},
            )
        except httpx.RequestError:
            return []
        if response.status_code != 200:
            return []
        return response.json().get("items", [])

    async def get_animes_by_ids(self, ids: list[int]) -> list:
        if not ids:
            return []
        try:
            response = await self.client.get(
                f"{settings.anime_service}/anime/by-ids",
                params={"ids": ",".join(str(i) for i in ids)},
            )
        except httpx.RequestError:
            return []
        return response.json() if response.status_code == 200 else []

    async def get_main_page_data(self, user_id: str = "") -> dict:
        # Первая волна — параллельно
        recommendations_raw, popular, news = await asyncio.gather(
            self.get_recommendations(user_id),
            self.get_popular(),
            self.get_news(),
        )

        # Достаём id рекомендаций
        recommended_ids = [r["id"] for r in recommendations_raw if "id" in r]

        # Вторая волна — только если есть id
        recommended_animes = await self.get_animes_by_ids(recommended_ids)

        return {
            "recommended": recommended_animes,
            "popular": popular,
            "news": news,
        }


main_service = MainService()