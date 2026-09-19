from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from repositories.database import Base


class Viewing(Base):
    __tablename__ = "viewings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    cinema: Mapped[str] = mapped_column(String(100), nullable=False)
    viewing_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    film_name: Mapped[str] = mapped_column(String(200), nullable=False)
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
