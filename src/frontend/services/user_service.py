import asyncio
import httpx
from src.frontend.config.settings import settings


async def fetch_user_info(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{settings.user_service}/user/profile/me", headers=headers)
            return r.json() if r.status_code == 200 else {}
        except httpx.RequestError:
            return {}


async def fetch_user_favorites(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{settings.user_service}/user/favorites/me", headers=headers)
            return r.json() if r.status_code == 200 else {'favorites': []}
        except httpx.RequestError:
            return {'favorites': []}


async def fetch_user_sessions(access_token: str) -> list:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{settings.user_service}/user/sessions", headers=headers)
            return r.json() if r.status_code == 200 else []
        except httpx.RequestError:
            return []