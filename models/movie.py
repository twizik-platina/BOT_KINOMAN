from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Movie:
    id: int
    title: str
    description: str = ""
    poster_url: str | None = None
    premiere_date: datetime | None = None
