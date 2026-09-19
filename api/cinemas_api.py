import html
import logging
import re
from datetime import date, datetime, time, timedelta, timezone

import requests

from models.cinema import Cinema
from models.city import City
from models.movie import Movie


logger = logging.getLogger(__name__)


class CinemasApiError(Exception):
    pass


class UnsupportedCityError(Exception):
    pass


def _normalize_city(value: str) -> str:
    return (
        value.casefold()
        .replace("ё", "е")
        .replace("-", " ")
        .strip()
    )


def _plain_text(value: str | None) -> str:
    if not value:
        return ""

    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _looks_like_cinema(title: str) -> bool:
    """Отсекает музеи, киностудии, парки и другие места из категории cinema."""
    value = _normalize_city(title)

    excluded = (
        "киностудия",
        "парк искусств",
        "планетарий",
        "музей кино",
        "культурный центр",
        "дворец молодежи",
        "дворец молодёжи",
        "креативное пространство",
        "выставочный центр",
    )

    if any(marker in value for marker in excluded):
        return False

    cinema_markers = (
        "кинотеатр",
        "киноцентр",
        "кинозал",
        "синема",
        "cinema",
        "киномакс",
        "каро",
        "формула кино",
        "пять звезд",
        "пять звёзд",
        "иллюзион",
        "пионер",
        "художественный",
        "аврора",
        "родина",
        "дом кино",
        "окко",
    )

    return any(marker in value for marker in cinema_markers)


class CinemasApi:
    BASE_URL = "https://kudago.com/public-api/v1.4"

    SUPPORTED_CITIES = {
        "москва": ("msk", "Москва", 55.7558, 37.6176),
        "санкт петербург": ("spb", "Санкт-Петербург", 59.9343, 30.3351),
        "санктпетербург": ("spb", "Санкт-Петербург", 59.9343, 30.3351),
        "спб": ("spb", "Санкт-Петербург", 59.9343, 30.3351),
        "казань": ("kzn", "Казань", 55.7961, 49.1064),
        "екатеринбург": ("ekb", "Екатеринбург", 56.8389, 60.6057),
        "нижний новгород": ("nnv", "Нижний Новгород", 56.2965, 43.9361),
    }

    CITY_UTC_OFFSETS = {
        "msk": 3,
        "spb": 3,
        "kzn": 3,
        "nnv": 3,
        "ekb": 5,
    }

    def __init__(self, timeout: int = 10):
        self.timeout = max(5, timeout)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Bot-Kinoman/1.0",
                "Accept": "application/json",
            }
        )

        self.direct_session = requests.Session()
        self.direct_session.trust_env = False
        self.direct_session.headers.update(self.session.headers)

    def _get(
        self,
        path: str,
        params: dict | None = None,
    ) -> dict | list:
        url = f"{self.BASE_URL}{path}"
        last_error: Exception | None = None

        for session in (self.session, self.direct_session):
            try:
                response = session.get(
                    url,
                    params=params,
                    timeout=(5, self.timeout),
                )
                response.raise_for_status()
                return response.json()

            except (requests.Timeout, requests.ConnectionError) as exc:
                last_error = exc

            except requests.HTTPError as exc:
                status = exc.response.status_code if exc.response is not None else "?"
                raise CinemasApiError(
                    f"KudaGo вернул HTTP-ошибку {status}"
                ) from exc

            except ValueError as exc:
                raise CinemasApiError(
                    "KudaGo вернул некорректный ответ"
                ) from exc

        raise CinemasApiError(
            "Не удалось получить данные KudaGo"
        ) from last_error

    def find_supported_city(
        self,
        city_name: str,
    ) -> tuple[City, str] | None:
        data = self.SUPPORTED_CITIES.get(_normalize_city(city_name))

        if data is None:
            return None

        slug, canonical_name, lat, lng = data
        return City(canonical_name, lat, lng), slug

    def get_location_slug(self, city_name: str) -> str:
        supported = self.find_supported_city(city_name)

        if supported is None:
            raise UnsupportedCityError(
                "Для этого города киноафиша недоступна."
            )

        _, slug = supported
        return slug

    def get_cinemas(self, location_slug: str) -> list[Cinema]:
        """Возвращает только реальные кинотеатры с актуальными показами."""
        cinemas = self._get_cinemas_from_showings(location_slug)

        if cinemas:
            return cinemas[:3]

        cinemas = self._get_cinemas_from_places(location_slug)

        if cinemas:
            return cinemas[:3]

        raise CinemasApiError(
            "Кинотеатры с актуальными сеансами не найдены."
        )

    def _get_cinemas_from_showings(
        self,
        location_slug: str,
    ) -> list[Cinema]:
        now = datetime.now(timezone.utc)
        week_later = now + timedelta(days=7)

        try:
            data = self._get(
                "/movie-showings/",
                {
                    "lang": "ru",
                    "location": location_slug,
                    "actual_since": int(now.timestamp()),
                    "actual_until": int(week_later.timestamp()),
                    "expand": "place",
                    "fields": "id,place,datetime",
                    "order_by": "datetime",
                    "page_size": 100,
                },
            )
        except CinemasApiError as exc:
            logger.warning("Не удалось получить показы KudaGo: %s", exc)
            return []

        result: list[Cinema] = []
        seen_ids: set[int] = set()

        for showing in data.get("results", []):
            place = showing.get("place") or {}
            place_id = place.get("id")
            title = (place.get("title") or "").strip()

            if not place_id or place_id in seen_ids:
                continue

            if place.get("is_closed") is True:
                continue

            if not _looks_like_cinema(title):
                continue

            seen_ids.add(int(place_id))
            result.append(
                Cinema(
                    id=int(place_id),
                    title=title,
                    address=(place.get("address") or "Адрес не указан").strip(),
                )
            )

            if len(result) == 3:
                break

        return result

    def _get_cinemas_from_places(
        self,
        location_slug: str,
    ) -> list[Cinema]:
        try:
            data = self._get(
                "/places/",
                {
                    "lang": "ru",
                    "location": location_slug,
                    "categories": "cinema",
                    "fields": "id,title,address,is_closed",
                    "page_size": 100,
                    "order_by": "id",
                },
            )
        except CinemasApiError as exc:
            logger.warning("Не удалось получить места KudaGo: %s", exc)
            return []

        result: list[Cinema] = []

        for item in data.get("results", []):
            title = (item.get("title") or "").strip()

            if item.get("is_closed") is True:
                continue

            if not _looks_like_cinema(title):
                continue

            try:
                cinema_id = int(item["id"])
            except (KeyError, TypeError, ValueError):
                continue

            result.append(
                Cinema(
                    id=cinema_id,
                    title=title,
                    address=(item.get("address") or "Адрес не указан").strip(),
                )
            )

            if len(result) == 3:
                break

        return result

    def _date_timestamps(
        self,
        location_slug: str,
        selected_date: date,
    ) -> tuple[int, int]:
        utc_offset = self.CITY_UTC_OFFSETS.get(location_slug, 3)
        local_tz = timezone(timedelta(hours=utc_offset))

        start = datetime.combine(
            selected_date,
            time.min,
            tzinfo=local_tz,
        )
        end = datetime.combine(
            selected_date,
            time.max,
            tzinfo=local_tz,
        )

        return int(start.timestamp()), int(end.timestamp())

    def get_movies_for_cinema_date(
        self,
        location_slug: str,
        cinema_id: int,
        selected_date: date,
    ) -> list[Movie]:
        actual_since, actual_until = self._date_timestamps(
            location_slug,
            selected_date,
        )

        # /movies/ использует параметр place, а не place_id.
        try:
            data = self._get(
                "/movies/",
                {
                    "lang": "ru",
                    "location": location_slug,
                    "place": cinema_id,
                    "actual_since": actual_since,
                    "actual_until": actual_until,
                    "fields": "id,title,description,body_text,poster",
                    "text_format": "text",
                    "page_size": 10,
                },
            )

            movies = self._movies_from_movies_endpoint(data)

            if movies:
                return movies[:5]

        except CinemasApiError as exc:
            logger.warning("Не удалось получить фильмы KudaGo: %s", exc)

        try:
            data = self._get(
                "/movie-showings/",
                {
                    "lang": "ru",
                    "location": location_slug,
                    "place_id": cinema_id,
                    "actual_since": actual_since,
                    "actual_until": actual_until,
                    "expand": "movie",
                    "fields": "id,movie,datetime,price",
                    "order_by": "datetime",
                    "page_size": 100,
                },
            )

            return self._movies_from_showings(data)[:5]

        except CinemasApiError as exc:
            raise CinemasApiError(
                "Не удалось получить фильмы в прокате."
            ) from exc

    def _movies_from_movies_endpoint(
        self,
        data: dict | list,
    ) -> list[Movie]:
        if isinstance(data, list):
            items = data
        else:
            items = data.get("results", [])

        movies: list[Movie] = []
        seen_ids: set[int] = set()

        for item in items:
            movie_id = item.get("id")

            if not movie_id:
                continue

            try:
                movie_id = int(movie_id)
            except (TypeError, ValueError):
                continue

            if movie_id in seen_ids:
                continue

            seen_ids.add(movie_id)
            poster = item.get("poster") or {}

            movies.append(
                Movie(
                    id=movie_id,
                    title=item.get("title") or "Без названия",
                    description=(
                        _plain_text(
                            item.get("description")
                            or item.get("body_text")
                        )
                        or "Описание отсутствует."
                    ),
                    poster_url=poster.get("image"),
                )
            )

        return movies

    def _movies_from_showings(
        self,
        data: dict | list,
    ) -> list[Movie]:
        if isinstance(data, list):
            items = data
        else:
            items = data.get("results", [])

        movies: list[Movie] = []
        seen_ids: set[int] = set()

        for showing in items:
            movie_data = showing.get("movie") or {}
            movie_id = movie_data.get("id")

            if not movie_id:
                continue

            try:
                movie_id = int(movie_id)
            except (TypeError, ValueError):
                continue

            if movie_id in seen_ids:
                continue

            seen_ids.add(movie_id)
            poster = movie_data.get("poster") or {}

            movies.append(
                Movie(
                    id=movie_id,
                    title=movie_data.get("title") or "Без названия",
                    description=(
                        _plain_text(
                            movie_data.get("description")
                            or movie_data.get("body_text")
                        )
                        or "Описание отсутствует."
                    ),
                    poster_url=poster.get("image"),
                )
            )

        return movies
