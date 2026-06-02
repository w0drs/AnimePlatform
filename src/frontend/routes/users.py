from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form

from typing import Optional
from pathlib import Path

from src.frontend.services.jwt_service import jwt_service
from src.frontend.schemas import users
from src.frontend.services.user_service import *
from src.frontend.services.auth_decorator import require_auth
from src.frontend.services.anime_service import anime_service

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/profile", response_class=HTMLResponse)
@require_auth
async def profile(
        request: Request,
        tab: str = "favorites",
        error: Optional[str] = None,
        payload: dict = None
):
    access_token = request.cookies.get("access_token")
    if not payload:
        return RedirectResponse(url="/login", status_code=302)

    """
    GET /profile - Показывает HTML страницу с формой профиля пользователя
    """
    payload, needs_refresh = await jwt_service.verify(request)
    if needs_refresh:
        return RedirectResponse(url=f"/refresh?next=/profile", status_code=302)

    is_authorized, is_admin = True, payload["role"] in (users.RoleADMIN, users.RoleMODER)

    user = await fetch_user_info(access_token)
    if not user:
        return RedirectResponse(url=f"/refresh?next=/profile", status_code=302)

    favorites, sessions = {}, {}
    if tab == "favorites":
        favorites_ids = await fetch_user_favorites(access_token)
        favorites = await anime_service.get_animes_by_ids([item['AnimeID'] for item in favorites_ids.get('favorites')])
    elif tab == "sessions":
        sessions = await fetch_user_sessions(access_token)
    if sessions:
        sessions = sessions.get("sessions")
    return templates.TemplateResponse("profile.html", {
        # что всегда есть
        "request": request,
        "active_page": "profile",
        # авторизация
        "is_authorized": is_authorized,
        "is_admin": is_admin,
        # для самой конкретной страницы
        "tab": tab,
        "user": user,
        "favorites": favorites,
        "sessions": sessions,
    }
)

@router.post("/logout")
@require_auth
async def logout(request: Request, payload: dict = None):
    access_token = request.cookies.get("access_token")
    if not payload:
        return RedirectResponse(url="/login", status_code=302)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.auth_service}/auth/logout",
                cookies=request.cookies,
                headers={"Authorization": f'Bearer {access_token}'}
            )
        except Exception as e:
            print("exception", e)

    if response.status_code != 200:
        return RedirectResponse(url="/main", status_code=302)

    resp = RedirectResponse(url="/main", status_code=302)

    resp.set_cookie("refresh", "", max_age=0, httponly=True, samesite="strict", path="/")
    resp.set_cookie("access_token", "", max_age=0, httponly=True, samesite="lax", path="/")
    return resp

@router.post("/settings/profile")
@require_auth
async def update_profile(
        request: Request,
        first_name: str = Form(default=""),
        description: str = Form(default=""),
        icon_url: str = Form(default=""),
        payload: dict = None
):
    access_token = request.cookies.get("access_token")
    if not payload:
        return RedirectResponse(url="/login", status_code=302)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.user_service}/user/profile/me",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "first_name": first_name,
                    "description": description,
                    "icon_url": icon_url,
                },
            )
        except httpx.RequestError:
            return RedirectResponse(url="/profile?error=Service unavailable", status_code=302)

    if response.status_code != 200:
        return RedirectResponse(url="/profile?error=Failed to update profile", status_code=302)

    return RedirectResponse(url="/profile", status_code=302)

@router.post("/settings/sessions/delete-all")
@require_auth
async def delete_all_sessions(request: Request, payload: dict = None):
    access_token = request.cookies.get("access_token")
    if not payload:
        return RedirectResponse(url="/login", status_code=302)

    async with httpx.AsyncClient() as client:
        try:
            await client.delete(
                f"{settings.auth_service}/user/sessions",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.RequestError:
            pass

    # Удаляем куки и редиректим на логин
    resp = RedirectResponse(url="/main", status_code=302)
    resp.set_cookie("access_token", "", max_age=0, httponly=True, samesite="lax", path="/")
    resp.set_cookie("refresh", "", max_age=0, httponly=True, samesite="strict", path="/")
    return resp


@router.post("/settings/password")
@require_auth
async def update_password(
        request: Request,
        old_password: str = Form(...),
        new_password: str = Form(...),
        payload: dict = None
):
    access_token = request.cookies.get("access_token")
    if not payload:
        return RedirectResponse(url="/login", status_code=302)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.auth_service}/auth/changepass",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "old_password": old_password,
                    "new_password": new_password,
                },
            )
        except httpx.RequestError:
            return RedirectResponse(url="/profile?tab=settings&error=Service unavailable", status_code=302)
    if response.status_code == 400:
        return RedirectResponse(url="/profile?tab=settings&error=Пароли совпадают", status_code=302)
    if response.status_code == 401:
        return RedirectResponse(url="/profile?tab=settings&error=Неверный текущий пароль", status_code=302)
    if response.status_code != 200:
        return RedirectResponse(url="/profile?tab=settings&error=Не удалось изменить пароль", status_code=302)

    # После смены пароля разлогиниваем — токены инвалидированы
    resp = RedirectResponse(url="/profile?tab=settings", status_code=302)
    return resp

@router.post("/settings/delete")
@require_auth
async def delete_account(request: Request, payload: dict = None):
    access_token = request.cookies.get("access_token")
    if not payload:
        return RedirectResponse(url="/login", status_code=302)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{settings.user_service}/user/profile/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.RequestError:
            return RedirectResponse(url="/profile?tab=settings&error=Service unavailable", status_code=302)

    if response.status_code != 204:
        return RedirectResponse(url="/profile?tab=settings&error=Не удалось удалить аккаунт", status_code=302)

    resp = RedirectResponse(url="/main", status_code=302)
    resp.set_cookie("access_token", "", max_age=0, httponly=True, samesite="lax", path="/")
    resp.set_cookie("refresh", "", max_age=0, httponly=True, samesite="strict", path="/")
    return resp
