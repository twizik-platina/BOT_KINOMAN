import logging

import requests

from models.city import City


logger = logging.getLogger(__name__)


class CityApiError(Exception):
    pass


class CitiesApi:
    # secure.geonames.org — основной адрес.
    # http://api.geonames.org — резервный, потому что HTTPS у api.geonames.org
    # на некоторых системах даёт ошибку сертификата.
    SEARCH_URLS = (
        "https://secure.geonames.org/searchJSON",
        "http://api.geonames.org/searchJSON",
    )

    def __init__(self, username: str, timeout: int = 10):
        self.username = username
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Bot-Kinoman/1.0"})

    def find_city(self, city_name: str) -> City | None:
        city_name = city_name.strip()

        if not city_name:
            return None

        params = {
            "q": city_name,
            "maxRows": 5,
            "featureClass": "P",
            "country": "RU",
            "lang": "ru",
            "username": self.username,
        }

        last_error: Exception | None = None

        for url in self.SEARCH_URLS:
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code == 401:
                    raise CityApiError(
                        "GeoNames отклонил запрос. "
                        "Проверьте username и включён ли Free Webservice."
                    )

                response.raise_for_status()
                data = response.json()

                if "status" in data:
                    message = data["status"].get(
                        "message",
                        "Неизвестная ошибка GeoNames",
                    )
                    raise CityApiError(f"Ошибка GeoNames: {message}")

                cities = data.get("geonames", [])

                if not cities:
                    return None

                item = cities[0]

                return City(
                    name=item["name"],
                    lat=float(item["lat"]),
                    lng=float(item["lng"]),
                )

            except CityApiError:
                raise
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                last_error = exc
                logger.warning("GeoNames %s недоступен: %s", url, exc)

        raise CityApiError(
            "Не удалось подключиться к GeoNames. "
            "Проверьте интернет/VPN и настройки GeoNames."
        ) from last_error
