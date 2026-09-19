from dataclasses import dataclass


@dataclass(slots=True)
class City:
    name: str
    lat: float
    lng: float
