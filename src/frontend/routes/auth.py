from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.frontend.services.jwt_service import jwt_service
from src.frontend.config.settings import settings
from src.frontend.services.auth_service import auth_service

from typing import Optional
from pathlib import Path
import httpx

router = APIRouter()
templates = Jinja2Templates(directory=f"{Path(__file__).resolve().parent.resolve().parent}/templates")
AUTH_SERVICE_URL = settings.auth_service


@router.get("/login", response_class=HTMLResponse)
async def login_page(
        request: Request,
        next: str = "/main",
        error: Optional[str] = None
):
    """
    GET /login - Показывает HTML форму логина
    """
    payload, needs_refresh = await jwt_service.verify(request)

    resp = templates.TemplateResponse("login.html",
    {
        "request": request,
        "error": error,
        "next": next,
    })

    if not payload and request.cookies.get('access_token'):
        resp.set_cookie("access_token", "", max_age=0, httponly=True, samesite="lax", path="/")

    return resp

@router.post("/login")
async def login(
        request: Request,
        next: str = "/main",
        email: str = Form(...),
        password: str = Form(...)
):
    if request.cookies.get("access_token"):
        return RedirectResponse(url=next, status_code=302)

    user_agent = request.headers.get("user-agent", "")
    real_ip = (
            request.headers.get('X-Real-IP') or
            request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            (request.client.host if request.client else "unknown")
    )

    try:
        response = await auth_service.login(email, password, real_ip, user_agent)
        access_token = response.access_token
        refresh_token = response.refresh_token

        resp = RedirectResponse(url=next, status_code=302)

        resp.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=settings.env == "production",
            samesite="lax",
            max_age=15 * 60,  # 15 минут
        )

        if refresh_token:
            resp.set_cookie(
                key="refresh",
                value=refresh_token,
                httponly=True,
                secure=settings.env == "production",
                samesite="lax",
                max_age=7 * 24 * 60 * 60,  # 7 дней
                path="/refresh"
            )

        return resp

    except httpx.TimeoutException:
        return RedirectResponse(
            url=f"/login?next={next}&error=Service unavailable, please try again",
            status_code=302
        )
    except Exception as e:
        print(f"Login error: {e}")
        return RedirectResponse(
            url=f"/login?next={next}&error=Something went wrong",
            status_code=302

)

@router.get("/register")
async def register_get(request: Request, error: str = None):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "active_page": "register",
        "is_authorized": False,
        "is_admin": False,
        "error": error,
        "form": {},
    })

@router.post("/register")
async def register_post(
        request: Request,
        login: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
):
    icon_url = settings.default_user_icon_name
    first_name = "Anonim"
    description = ""

    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "is_authorized": False,
            "is_admin": False,
            "error": "Пароли не совпадают",
            "form": {"login": login, "email": email},
        })

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.auth_service}/auth/register",
                json={"login": login, "email": email, "password": password, "icon_url": icon_url,
                      "first_name": first_name, "description": description},
            )
        except httpx.RequestError:
            return RedirectResponse(url="/register?error=Service unavailable", status_code=302)

    if response.status_code == 409:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "is_authorized": False,
            "is_admin": False,
            "error": "Email или логин уже заняты",
            "form": {"login": login, "email": email},
        })
    if response.status_code != 201:
        return RedirectResponse(url="/register?error=Ошибка регистрации", status_code=302)

    return RedirectResponse(url="/login", status_code=302)

@router.get("/refresh")
async def refresh_get(request: Request, next: str = "/main"):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.auth_service}/auth/refresh",
                cookies=request.cookies,
            )
        except httpx.RequestError:
            return RedirectResponse(url="/login", status_code=302)
    if response.status_code != 200:
        return RedirectResponse(url="/login", status_code=302)
    data = response.json()
    new_access_token = data.get("access_token")

    resp = RedirectResponse(url=next, status_code=303)

    resp.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.env == "production",
        samesite="lax",
        max_age=15 * 60,
    )

    # Пробрасываем Set-Cookie от auth сервиса (новый refresh)
    for header_value in response.headers.get_list("set-cookie"):
        resp.raw_headers.append((b"set-cookie", header_value.encode()))
    return resp
