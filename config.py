from dataclasses import dataclass


# Настройки проекта
TG_BOT_TOKEN = "8572928625:AAHa0Tz8ZoNdUnvwj3Z3QgMfkGPY49DVfE4"
DATABASE_URL = "postgresql+psycopg://postgres:12345@localhost:5432/kinoman"
GEONAMES_USERNAME = "twizya"
KINOPOISK_API_KEY = "PV2QTP0-3GGMXH0-GBARRB7-DDWE6C6"
REQUEST_TIMEOUT = 30


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_url: str
    geonames_username: str
    kinopoisk_api_key: str
    request_timeout: int = 10

    @classmethod
    def from_file(cls) -> "Config":
        values = {
            "bot_token": TG_BOT_TOKEN.strip(),
            "database_url": DATABASE_URL.strip(),
            "geonames_username": GEONAMES_USERNAME.strip(),
            "kinopoisk_api_key": KINOPOISK_API_KEY.strip(),
        }

        not_filled = [
            name
            for name, value in values.items()
            if not value or value.startswith("PASTE_")
        ]
        if not_filled:
            readable = ", ".join(not_filled)
            raise RuntimeError(
                "Не заполнены настройки: " + readable
            )

        return cls(
            **values,
            request_timeout=REQUEST_TIMEOUT,
        )
