from dataclasses import dataclass


@dataclass(slots=True)
class Cinema:
    id: int
    title: str
    address: str
