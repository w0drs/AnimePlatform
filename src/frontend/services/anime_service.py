import asyncio
import httpx

from src.frontend.config.settings import settings
from src.frontend.utils.utils import format_time_ago

class AnimeService:

    async def get_anime(self, anime_id: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{settings.anime_service}/anime/{anime_id}")
            except httpx.RequestError:
                return None
        return response.json() if response.status_code == 200 else None

    async def get_recommendations(self, anime_id: str, limit: int = 10) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.recommends_service}/recommend/anime/{anime_id}",
                    params={"limit": limit},
                )
            except httpx.RequestError:
                return {}
        return response.json() if response.status_code == 200 else {}

    async def get_comments(self, anime_id: str, page: int = 1) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.comments_service}/comments/anime/{anime_id}",
                    params={"page": page},
                )
            except httpx.RequestError:
                return {}
        return response.json() if response.status_code == 200 else {}

    async def get_animes_by_ids(self, ids: list[int]) -> list:
        if not ids:
            return []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.anime_service}/anime/by-ids",
                    params={"ids": ",".join(str(i) for i in ids)},
                )
            except httpx.RequestError:
                return []
        return response.json() if response.status_code == 200 else []

    async def get_users_batch(self, user_ids: list[str]) -> dict:
        if not user_ids:
            return {}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.user_service}/users/batch",
                    json={"users_id": user_ids},
                )
            except httpx.RequestError:
                return {}
        return response.json() if response.status_code == 200 else {}

    async def check_favorite(self, anime_id: str, access_token: str) -> bool:
        if not access_token:
            return False
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.user_service}/user/favorites/me/{anime_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                return response.status_code == 200
            except httpx.RequestError:
                return False

    async def enrich_comments(self, comments_raw: dict) -> list:
        comments = comments_raw.get("comments", [])
        user_ids = list({c["UserID"] for c in comments if c.get("UserID")})
        users_batch = await self.get_users_batch(user_ids)
        users_map = {u["ID"]: u for u in users_batch.get("users", []) if "ID" in u}

        return [
            {
                "id": c.get("ID"),
                "username": users_map.get(c.get("UserID"), {}).get("Login", "Аноним"),
                "user_avatar": users_map.get(c.get("UserID"), {}).get("IconUrl", ""),
                "text": c.get("Text", ""),
                "created_at": format_time_ago(c.get("CreatedAt", "")),
            }
            for c in comments
        ]


    async def get_anime_page_data(self, anime_id: str, page: int = 1, limit: int = 10, access_token: str = None) -> dict:
        # Первая волна — параллельно
        anime, recommendations_raw, comments_raw, is_favorite = await asyncio.gather(
            self.get_anime(anime_id),
            self.get_recommendations(anime_id, limit),
            self.get_comments(anime_id, page),
            self.check_favorite(anime_id, access_token),
        )

        recommended_ids = [
            r["id"] for r in recommendations_raw.get("recommendations", []) if "id" in r
        ]

        # Вторая волна — параллельно
        recommended_animes, comments_with_users = await asyncio.gather(
            self.get_animes_by_ids(recommended_ids),
            self.enrich_comments(comments_raw),
        )

        return {
            "is_favorite": is_favorite,
            "anime": anime,
            "recommendations": recommended_animes,
            "comments": comments_with_users,
        }


anime_service = AnimeService()