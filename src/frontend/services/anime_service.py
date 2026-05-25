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

    async def get_anime_page_data(self, anime_id: str, page: int = 1, limit: int = 10) -> dict:
        # Первая волна — параллельно
        anime, recommendations_raw, comments_raw = await asyncio.gather(
            self.get_anime(anime_id),
            self.get_recommendations(anime_id, limit),
            self.get_comments(anime_id, page),
        )

        # Достаём id из результатов
        recommended_ids = [
            r["id"] for r in recommendations_raw.get("recommendations", []) if "id" in r
        ]
        comment_user_ids = list({
            c["UserID"] for c in comments_raw.get("comments", []) if c.get("UserID")
        })

        # Вторая волна — параллельно
        recommended_animes, users_batch = await asyncio.gather(
            self.get_animes_by_ids(recommended_ids),
            self.get_users_batch(comment_user_ids),
        )

        # Мапа user_id -> user для шаблона
        users_map = {
            u["ID"]: u for u in users_batch.get("users", []) if "ID" in u
        }
        comments = comments_raw.get("comments", [])
        comments_with_users = [
            {
                "id": c.get("ID"),
                "username": users_map.get(c.get("UserID"), {}).get("Login", c.get("ID")),
                "user_avatar": users_map.get(c.get("UserID"), {}).get("IconUrl", settings.default_user_icon_name),
                "text": c.get("Text", ""),
                "created_at": format_time_ago(c.get("CreatedAt", "")),
            }
            for c in comments
        ]

        return {
            "anime": anime,
            "recommendations": recommended_animes,
            "comments": comments_with_users,
        }


anime_service = AnimeService()