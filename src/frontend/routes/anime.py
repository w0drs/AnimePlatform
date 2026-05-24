from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Optional
from pathlib import Path

from src.frontend.services.jwt_service import jwt_service
from src.frontend.services.auth_service import auth_service
from src.frontend.schemas import users

BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.globals.update(max=max, min=min)

@router.get("/main", response_class=HTMLResponse)
async def main(
        request: Request,
        error: Optional[str] = None
):
    """
    GET /main - Показывает HTML форму главной страницы
    """
    payload, needs_refresh = await jwt_service.verify(request)
    is_authorized, is_admin = False, False

    if not needs_refresh:
        is_authorized = True
        is_admin = payload["role"] == users.RoleADMIN or payload["role"] == users.RoleMODER

    return templates.TemplateResponse("main.html", {
        "request": request,
        "active_page": "home",

        "is_authorized": is_authorized,
        "is_admin": is_admin,

        "recommended": [...],  # список словарей с полями title, year, rating, image
        "popular": [...],

    }
)


@router.get("/anime/{anime_id}", response_class=HTMLResponse)
def anime_page(
        request: Request,
        anime_id: int,
        error: Optional[str] = None
):
    """
    GET /anime/{anime_id} - Страница детального просмотра аниме
    """

    # Заглушка для данных аниме (потом замените на реальные из БД)
    anime_data = {
        "id": anime_id,
        "title_english": "Code Geass: Lelouch of the Rebellion",
        "type": "TV Сериал",
        "episodes": "25 (Сезон 1) + 25 (Сезон 2)",
        "duration": "24 мин. / эп.",
        "rating": "9.0",
        "year": "2006-2008",
        "synopsis": "В 2010 году Священная Британская Империя завоевывает Японию, переименовывая её в Зону 11. Бывший принц Британии Лелуш Ламперуж после встречи с загадочной девушкой Си Си получает силу 'Гиас' — способность подчинять волю любого человека. Теперь под маской таинственного повстанца Зеро он начинает войну против Британской Империи, чтобы отомстить за свою мать и создать мир, в котором его младшая сестра Нуннали сможет жить счастливо.",
        "background": None,
        "trailer_url": "https://www.youtube.com/watch?v=hlxZIEBk6ps",
        "image_webp_large_url": "code_gias.jpg"
    }

    # Заглушка для жанров
    genres = ["Экшен", "Драма", "Меха", "Психологическое", "Военное"]

    # Заглушка для студий
    studios = ["Sunrise"]

    # Заглушка для похожих аниме
    similar_anime = [
        {"id": 1, "title_english": "Death Note", "year": "2006", "image_webp_large_url": ""},
        {"id": 2, "title_english": "Guilty Crown", "year": "2011", "image_webp_large_url": ""},
        {"id": 3, "title_english": "Eureka Seven", "year": "2005", "image_webp_large_url": ""},
        {"id": 4, "title_english": "Mobile Suit Gundam 00", "year": "2007", "image_webp_large_url": ""},
        {"id": 5, "title_english": "Classroom of the Elite", "year": "2017", "image_webp_large_url": ""},
        {"id": 6, "title_english": "Legend of the Galactic Heroes", "year": "1988", "image_webp_large_url": ""},
    ]

    # Заглушка для комментариев
    comments = [
        {
            "id": 1,
            "username": "AnimePhilosopher",
            "created_at": "3 часа назад",
            "text": "Шедевр! Лелуш — один из лучших протагонистов в истории аниме. Концовка просто разрывает душу.",
            "user_avatar": "",
            "replies": [
                {
                    "id": 2,
                    "username": "CodeGeassFan",
                    "created_at": "2 часа назад",
                    "text": "Абсолютно согласен! Лелуш Ви Британия — гениальный стратег. Финал 'R2' стал легендарным.",
                    "user_avatar": "",
                    "tagged_username": None
                }
            ]
        },
        {
            "id": 3,
            "username": "MechaLover",
            "created_at": "1 день назад",
            "text": "Меха-дизайн отличный! Найтмеры выглядят очень круто. C.C. лучшая героиня!",
            "user_avatar": "",
            "replies": []
        },
        {
            "id": 4,
            "username": "NewWatcher",
            "created_at": "3 дня назад",
            "text": "Только начал смотреть. Немного старовато по рисовке, но сюжет захватывает с первых серий.",
            "user_avatar": "",
            "replies": []
        }
    ]

    total_pages = 1
    current_page = 1

    return templates.TemplateResponse("anime_detail.html", {
        "request": request,
        "active_page": "catalog",
        "is_authorized": False,
        "is_admin": False,
        "user_avatar": None,

        # Данные аниме
        "anime": anime_data,
        "genres": genres,
        "studios": studios,

        # Похожие аниме
        "similar_anime": similar_anime,

        # Комментарии
        "comments": comments,
        "total_pages": total_pages,
        "current_page": current_page,
    })

# API роуты для комментариев (заглушки)
@router.post("/api/comments/add", name="api_add_comment")
async def api_add_comment(comment, request: Request):
    """Заглушка для добавления комментария"""
    # Здесь будет реальная логика сохранения комментария
    return {
        "success": True,
        "message": "Комментарий добавлен (заглушка)",
        "comment_id": 999
    }


@router.get("/api/comments", name="api_get_comments")
async def api_get_comments(
    request: Request,
    anime_id: int,
    page: int = 1
):
    """Заглушка для получения комментариев"""
    return {
        "success": True,
        "comments": [],
        "total_pages": 1,
        "current_page": page
    }


@router.get("/catalog", response_class=HTMLResponse, name="catalog")
def catalog(
        request: Request,
        year: Optional[str] = None,
        genre: Optional[str] = None,
        rating: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        error: Optional[str] = None
):
    """Страница каталога аниме"""

    # Заглушка для фильтров
    filters = {
        "year": year,
        "genre": genre,
        "rating": rating,
        "status": status,
        "search": search
    }

    # Заглушка для списка аниме (замените на реальные данные из БД)
    anime_list = [
        {"id": 1, "title_english": "Атака Титанов", "rating": "9.2", "image_webp_large_url": ""},
        {"id": 2, "title_english": "Магическая битва", "rating": "8.9", "image_webp_large_url": ""},
        {"id": 3, "title_english": "One Piece", "rating": "9.1", "image_webp_large_url": ""},
        {"id": 4, "title_english": "Тетрадь смерти", "rating": "9.0", "image_webp_large_url": ""},
        {"id": 5, "title_english": "Человек-бензопила", "rating": "8.6", "image_webp_large_url": ""},
        {"id": 6, "title_english": "Spy×Family", "rating": "8.8", "image_webp_large_url": ""},
    ]

    # Заглушка для жанров (замените на реальные данные из БД)
    all_genres = [
        {"id": 1, "name": "Экшен"},
        {"id": 2, "name": "Комедия"},
        {"id": 3, "name": "Драма"},
        {"id": 4, "name": "Романтика"},
        {"id": 5, "name": "Фэнтези"},
        {"id": 6, "name": "Научная фантастика"},
        {"id": 7, "name": "Ужасы"},
    ]

    total_count = len(anime_list)
    total_pages = 1
    current_page = page

    # Функция для обновления параметров запроса
    def update_query(**kwargs):
        params = {
            "year": year,
            "genre": genre,
            "rating": rating,
            "status": status,
            "search": search,
            "page": page
        }
        params.update(kwargs)
        # Убираем пустые значения
        params = {k: v for k, v in params.items() if v}
        return "&".join([f"{k}={v}" for k, v in params.items()])

    return templates.TemplateResponse("catalog.html", {
        "request": request,
        "active_page": "catalog",
        "is_authorized": False,
        "is_admin": False,
        "anime_list": anime_list,
        "all_genres": all_genres,
        "filters": filters,
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": current_page,
        "update_query": update_query,
    })


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