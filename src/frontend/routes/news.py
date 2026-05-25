from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.get("/news", response_class=HTMLResponse, name="news")
def news_page(
        request: Request,
        page: int = 1,
        error: Optional[str] = None
):
    """Страница новостей"""

    # Заглушка для списка новостей (замените на реальные данные из БД)
    news_list = [
        {
            "id": 1,
            "title": "Анонсирован второй сезон Solo Leveling",
            "date": "15 мая 2026 • 14:30",
            "created_at": "15 мая 2026 • 14:30",
            "excerpt": "Студия A-1 Pictures официально подтвердила выход второго сезона аниме 'Один уровень'. Премьера запланирована на январь 2025 года.",
            "content": "Студия A-1 Pictures официально подтвердила выход второго сезона аниме 'Один уровень'. Премьера запланирована на январь 2025 года. Режиссёрский состав остаётся прежним, а новый трейлер обещают показать в ближайшие недели.",
            "image_url": ""
        },
        {
            "id": 2,
            "title": "Магическая битва: третий сезон в разработке",
            "date": "14 мая 2026 • 10:15",
            "created_at": "14 мая 2026 • 10:15",
            "excerpt": "MAPPA объявила о начале работы над третьим сезоном 'Магической битвы'. Ожидается в 2026 году.",
            "content": "MAPPA объявила о начале работы над третьим сезоном 'Магической битвы'. Арка 'Игра на уничтожение' будет адаптирована с беспрецедентным качеством анимации. Ожидается в 2026 году.",
            "image_url": ""
        },
        {
            "id": 3,
            "title": "Re:Zero Season 3 — новый трейлер и дата премьеры",
            "date": "12 мая 2026 • 18:45",
            "created_at": "12 мая 2026 • 18:45",
            "excerpt": "Премьера состоится 2 октября 2024 года. Адаптация арки 'Жадность' и 'Боевой клич'.",
            "content": "Опубликован полноценный трейлер третьего сезона Re:Zero. Премьера состоится 2 октября 2024 года. Адаптация арки 'Жадность' и 'Боевой клич'. Новые персонажи и возвращение любимых героев.",
            "image_url": ""
        },
        {
            "id": 4,
            "title": "Фрирен: Провожающая в последний путь — новый рекорд",
            "date": "5 мая 2026 • 12:00",
            "created_at": "5 мая 2026 • 12:00",
            "excerpt": "Аниме 'Фрирен' вошло в топ-5 лучших аниме всех времён на MyAnimeList с рейтингом 9.34.",
            "content": "Аниме 'Фрирен' вошло в топ-5 лучших аниме всех времён на MyAnimeList с рейтингом 9.34. Фанаты ждут анонса второго сезона после успеха первого курса.",
            "image_url": ""
        },
        {
            "id": 5,
            "title": "One-Punch Man Season 3 — смена студии",
            "date": "10 мая 2026 • 09:30",
            "created_at": "10 мая 2026 • 09:30",
            "excerpt": "Третий сезон 'Ванпанчмена' будет создаваться студией J.C.Staff.",
            "content": "Третий сезон 'Ванпанчмена' будет создаваться студией J.C.Staff. Режиссёр — Томохиро Судзуки (Mob Psycho 100 II). Визуальный стиль обещает быть ближе к манге ONE. Премьера — 2025 год.",
            "image_url": ""
        },
        {
            "id": 6,
            "title": "Oshi no Ko Season 2 — официальный анонс",
            "date": "8 мая 2026 • 16:20",
            "created_at": "8 мая 2026 • 16:20",
            "excerpt": "Создатели 'Звёздного дитя' подтвердили второй сезон.",
            "content": "Создатели 'Звёздного дитя' подтвердили второй сезон. Сюжет продолжит арку сцены '2.5D'. Тизер-арт уже опубликован, дата выхода пока не объявлена.",
            "image_url": ""
        }
    ]

    total_count = len(news_list)
    total_pages = 1
    current_page = page

    return templates.TemplateResponse("news.html", {
        "request": request,
        "active_page": "news",
        "is_authorized": False,
        "is_admin": False,
        "news_list": news_list,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": current_page,
    })


@router.get("/news/{news_id}", response_class=HTMLResponse, name="news_detail")
def news_detail_page(
        request: Request,
        news_id: int,
        page: int = 1,
        error: Optional[str] = None
):
    """Страница отдельной новости"""

    # Заглушка для данных новости (замените на реальные данные из БД)
    news_data = {
        "id": news_id,
        "title": "Анонсирован второй сезон Solo Leveling",
        "date": "15 мая 2026 • 14:30",
        "created_at": "15 мая 2026 • 14:30",
        "author": "Редакция Kuronami",
        "content": """
            <p>Студия A-1 Pictures официально подтвердила выход второго сезона аниме <strong>"Один уровень"</strong> (Solo Leveling). Премьера запланирована на январь 2025 года.</p>

            <p>Режиссёрский состав остаётся прежним — работу над сериалом продолжит режиссёр Синсукэ Накамура. Сценарий снова напишет Ёсукэ Курода. Визуальный стиль и качество анимации обещают сохранить на уровне первого сезона.</p>

            <p>Первый трейлер второго сезона был показан на закрытом мероприятии Anime Expo 2024. Фанаты отметили новые эффекты и динамичные боевые сцены. Ожидается, что публичный трейлер появится в ближайшие недели.</p>

            <p>Напомним, что первый сезон "Один уровень" вышел в январе 2024 года и мгновенно стал хитом. Аниме получило высокие оценки как от критиков, так и от зрителей. Второй сезон будет адаптировать следующие главы манхвы, включая знаменитую арку "Остров Чеджу".</p>

            <p>Следите за обновлениями на Kuronami, чтобы не пропустить новые трейлеры и даты выхода!</p>
        """,
        "image_url": "",
        "tags": ["Solo Leveling", "Анонс", "A-1 Pictures"]
    }

    # Заглушка для комментариев
    comments = [
        {
            "id": 1,
            "username": "AnimeFan",
            "created_at": "3 часа назад",
            "text": "Наконец-то! Очень ждал второго сезона. Первый был просто великолепен!",
            "user_avatar": "",
            "replies": [
                {
                    "id": 2,
                    "username": "SungJinWoo",
                    "created_at": "2 часа назад",
                    "text": "Согласен! Арка на острове Чеджу будет эпичной!",
                    "user_avatar": "",
                    "tagged_username": None
                }
            ]
        },
        {
            "id": 3,
            "username": "WeebMaster",
            "created_at": "1 день назад",
            "text": "Интересно, сколько эпизодов будет? Надеюсь, не 12, а хотя бы 24.",
            "user_avatar": "",
            "replies": []
        }
    ]

    total_pages = 1
    current_page = page

    return templates.TemplateResponse("news_detail.html", {
        "request": request,
        "active_page": "news",
        "is_authorized": False,
        "is_admin": False,
        "user_avatar": None,
        "news": news_data,
        "comments": comments,
        "total_pages": total_pages,
        "current_page": current_page,
    })