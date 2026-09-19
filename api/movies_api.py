from datetime import date, datetime, timedelta

import requests

from models.movie import Movie


class MoviesApiError(Exception):
    pass


class MoviesApi:
    BASE_URL = "https://api.kinopoisk.dev/v1.4/movie"

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": self.api_key,
                "User-Agent": "Bot-Kinoman/1.0",
            }
        )

    def get_week_premieres(
        self,
        start_date: date | None = None,
    ) -> list[Movie]:
        start_date = start_date or date.today()
        end_date = start_date + timedelta(days=7)

        date_range = (
            f"{start_date.strftime('%d.%m.%Y')}-"
            f"{end_date.strftime('%d.%m.%Y')}"
        )

        params = {
            "page": 1,
            "limit": 5,
            "type": "movie",
            "premiere.russia": date_range,
            "sortField": "premiere.russia",
            "sortType": "1",
            "selectFields": [
                "id",
                "name",
                "shortDescription",
                "description",
                "poster",
                "premiere",
            ],
        }

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise MoviesApiError(
                "Не удалось получить список премьер Kinopoisk.dev"
            ) from exc

        movies: list[Movie] = []

        for item in data.get("docs", [])[:5]:
            title = item.get("name") or "Без названия"
            description = (
                item.get("shortDescription")
                or item.get("description")
                or "Описание отсутствует."
            )
            poster = item.get("poster") or {}
            premiere = item.get("premiere") or {}

            premiere_date = None
            raw_date = premiere.get("russia")

            if raw_date:
                try:
                    premiere_date = datetime.fromisoformat(
                        raw_date.replace("Z", "+00:00")
                    )
                except (TypeError, ValueError):
                    premiere_date = None

            movies.append(
                Movie(
                    id=int(item.get("id") or 0),
                    title=title,
                    description=description,
                    poster_url=poster.get("url"),
                    premiere_date=premiere_date,
                )
            )

        return movies
