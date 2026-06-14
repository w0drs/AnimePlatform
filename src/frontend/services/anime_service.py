import asyncio
import httpx
from typing import Optional, List

from src.frontend.config.settings import settings
from src.frontend.utils.utils import format_time_ago

ANIME_API_URL = settings.anime_service

async def get_genres_list() -> List[tuple]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/genres", timeout=10.0)
        if response.status_code == 200:
            return [(g['id'], g['name']) for g in response.json()]
        return []


async def get_themes_list() -> List[tuple]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/themes", timeout=10.0)
        if response.status_code == 200:
            return [(t['id'], t['name']) for t in response.json()]
        return []


async def get_demographics_list() -> List[tuple]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/demographics", timeout=10.0)
        if response.status_code == 200:
            return [(d['id'], d['name']) for d in response.json()]
        return []


async def get_studios_list() -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/studios", timeout=10.0)
        if response.status_code == 200:
            return [s['name'] for s in response.json()]
        return []


async def get_anime_by_id(anime_id: int) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ANIME_API_URL}/anime/{anime_id}", timeout=10.0)
        if response.status_code == 200:
            return response.json()
    return None




class AnimeService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

    async def get_anime(self, anime_id: str) -> dict | None:
        try:
            response = await self.client.get(f"{settings.anime_service}/anime/{anime_id}")
        except httpx.RequestError:
            return None
        return response.json() if response.status_code == 200 else None

    async def get_recommendations(self, anime_id: str, limit: int = 10) -> dict:
        try:
            response = await self.client.get(
                f"{settings.recommends_service}/recommend/anime/{anime_id}",
                params={"limit": limit},
            )
        except httpx.RequestError:
            return {}
        return response.json() if response.status_code == 200 else {}

    async def get_comments(self, anime_id: str, page: int = 1) -> dict:
        try:
            response = await self.client.get(
                f"{settings.comments_service}/comments/anime/{anime_id}",
                params={"page": page},
            )
        except httpx.RequestError:
            return {}
        return response.json() if response.status_code == 200 else {}

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

    async def get_users_batch(self, user_ids: list[str]) -> dict:
        if not user_ids:
            return {}
        try:
            response = await self.client.post(
                f"{settings.user_service}/users/batch",
                json={"users_id": user_ids},
            )
        except httpx.RequestError:
            return {}
        return response.json() if response.status_code == 200 else {}

    async def check_favorite(self, anime_id: str, access_token: str) -> bool:
        if not access_token:
            return False
        try:
            response = await self.client.get(
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