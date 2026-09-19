"""Сервисный слой Бота-Киномана.

UI не обращается к requests или SQLAlchemy напрямую.
Это соответствует трёхслойной архитектуре эталонного проекта:
UI -> services -> api/repositories.
"""

import logging
from dataclasses import dataclass
from datetime import date, datetime
from math import ceil

from api.cinemas_api import CinemasApi, UnsupportedCityError
from api.cities_api import CitiesApi, CityApiError
from api.movies_api import MoviesApi
from config import Config
from models.cinema import Cinema
from models.city import City
from models.movie import Movie
from models.viewing import Viewing
from repositories.database import Database
from repositories.viewings_repository import ViewingsRepository


logger = logging.getLogger(__name__)

HISTORY_PAGE_SIZE = 3

config = Config.from_file()

database = Database(config.database_url)
viewings_repository = ViewingsRepository(database)

cities_api = CitiesApi(
    username=config.geonames_username,
    timeout=config.request_timeout,
)
movies_api = MoviesApi(
    api_key=config.kinopoisk_api_key,
    timeout=config.request_timeout,
)
cinemas_api = CinemasApi(
    timeout=config.request_timeout,
)


@dataclass(slots=True)
class HistoryPage:
    items: list[Viewing]
    page: int
    total_pages: int


def prepare_database() -> None:
    database.check_connection()
    database.create_tables()


def get_week_premieres() -> list[Movie]:
    return movies_api.get_week_premieres()


def find_city(city_name: str) -> tuple[City | None, str | None]:
    city_name = city_name.strip()

    if not city_name:
        return None, None

    try:
        city = cities_api.find_city(city_name)
    except CityApiError as exc:
        # Если GeoNames временно заблокирован VPN, для поддерживаемых KudaGo
        # городов бот всё равно может продолжить работу.
        logger.warning(
            "GeoNames недоступен, проверяем локальный список KudaGo: %s",
            exc,
        )
        fallback = cinemas_api.find_supported_city(city_name)

        if fallback is not None:
            return fallback

        raise

    if city is None:
        return None, None

    try:
        location_slug = cinemas_api.get_location_slug(city.name)
    except UnsupportedCityError:
        # Иногда GeoNames возвращает вариант названия, отличный от введённого.
        fallback = cinemas_api.find_supported_city(city_name)

        if fallback is None:
            raise

        fallback_city, location_slug = fallback
        return fallback_city, location_slug

    return city, location_slug


def get_cinemas(location_slug: str) -> list[Cinema]:
    return cinemas_api.get_cinemas(location_slug)


def get_movies(
    location_slug: str,
    cinema_id: int,
    selected_date: date,
) -> list[Movie]:
    return cinemas_api.get_movies_for_cinema_date(
        location_slug,
        cinema_id,
        selected_date,
    )


def save_viewing(
    tg_user_id: int,
    city: City,
    cinema: Cinema,
    selected_date: date,
    movie: Movie,
) -> Viewing:
    viewing_date = datetime.combine(
        selected_date,
        datetime.min.time(),
    )

    return viewings_repository.create(
        tg_user_id=tg_user_id,
        city=city.name,
        cinema=cinema.title,
        viewing_date=viewing_date,
        film_name=movie.title,
    )


def get_history(
    tg_user_id: int,
    page: int,
) -> HistoryPage:
    total = viewings_repository.count_for_user(tg_user_id)
    total_pages = max(1, ceil(total / HISTORY_PAGE_SIZE))

    page = max(0, min(page, total_pages - 1))

    items = viewings_repository.get_for_user(
        tg_user_id,
        limit=HISTORY_PAGE_SIZE,
        offset=page * HISTORY_PAGE_SIZE,
    )

    return HistoryPage(
        items=items,
        page=page,
        total_pages=total_pages,
    )


def get_viewing(
    viewing_id: int,
    tg_user_id: int,
) -> Viewing | None:
    return viewings_repository.get_by_id_for_user(
        viewing_id,
        tg_user_id,
    )


def save_note(
    viewing_id: int,
    tg_user_id: int,
    note: str,
) -> Viewing | None:
    note = note.strip()

    if not note:
        raise ValueError("Заметка не должна быть пустой")

    if len(note) > 1000:
        raise ValueError("Заметка не должна превышать 1000 символов")

    return viewings_repository.update_note(
        viewing_id,
        tg_user_id,
        note,
    )
