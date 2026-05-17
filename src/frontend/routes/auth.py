from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from src.frontend.config.settings import settings
from typing import Optional

import httpx

router = APIRouter()
templates = Jinja2Templates(directory="/templates")
AUTH_SERVICE_URL = settings.auth_service


@router.get("/login", response_class=HTMLResponse)
async def login_page(
        request: Request,
        error: Optional[str] = None
):
    """
    GET /login - Показывает HTML форму логина
    """
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error}
    )


@router.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
):
    """
    POST /login - Отправляет данные в auth сервис
    """
    # Получаем User-Agent
    user_agent = request.headers.get("user-agent", "")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/login",
                json={
                    "email": email,
                    "password": password,
                    "user_agent": user_agent
                },
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": user_agent
                }
            )

        # Если auth сервис вернул ошибку
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Invalid credentials")
            return RedirectResponse(
                url=f"/login?error={error_detail}",
                status_code=302
            )

        # Получаем токены
        data = response.json()
        access_token = data.get("access_token")

        # Получаем refresh_token из cookies (если auth сервис установил)
        refresh_token = None
        for cookie in response.cookies:
            if cookie.key == "refresh_token":
                refresh_token = cookie.value
                break

        # Создаем HTML страницу с JavaScript для сохранения access_token
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting...</title>
        </head>
        <body>
            <script>
                // Сохраняем access_token в localStorage
                localStorage.setItem('access_token', '{access_token}');
                // Перенаправляем на главную
                window.location.href = '/';
            </script>
        </body>
        </html>
        """

        # Создаем ответ с установкой refresh_token cookie
        resp = HTMLResponse(content=html_content)

        if refresh_token:
            resp.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,  # True в production (HTTPS)
                samesite="lax",
                max_age=7 * 24 * 60 * 60,  # 7 дней
                path="/"
            )

        return resp

    except httpx.TimeoutException:
        return RedirectResponse(
            url="/login?error=Service unavailable, please try again",
            status_code=302
        )
    except Exception as e:
        print(f"Login error: {e}")
        return RedirectResponse(
            url="/login?error=Something went wrong",
            status_code=302
        )