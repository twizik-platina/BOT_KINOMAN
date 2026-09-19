from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from models.viewing import Viewing
from repositories.database import Database


class RepositoryError(Exception):
    pass


class ViewingsRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(
        self,
        tg_user_id: int,
        city: str,
        cinema: str,
        viewing_date: datetime,
        film_name: str,
    ) -> Viewing:
        viewing = Viewing(
            tg_user_id=tg_user_id,
            city=city,
            cinema=cinema,
            viewing_date=viewing_date,
            film_name=film_name,
            note=None,
        )

        try:
            with self.database.session() as session:
                session.add(viewing)
                session.commit()
                session.refresh(viewing)
                return viewing
        except SQLAlchemyError as exc:
            raise RepositoryError("Не удалось сохранить посещение") from exc

    def get_for_user(
        self,
        tg_user_id: int,
        limit: int,
        offset: int,
    ) -> list[Viewing]:
        try:
            with self.database.session() as session:
                stmt = (
                    select(Viewing)
                    .where(Viewing.tg_user_id == tg_user_id)
                    .order_by(Viewing.viewing_date.desc(), Viewing.id.desc())
                    .limit(limit)
                    .offset(offset)
                )
                return list(session.scalars(stmt).all())
        except SQLAlchemyError as exc:
            raise RepositoryError("Не удалось загрузить историю") from exc

    def count_for_user(self, tg_user_id: int) -> int:
        try:
            with self.database.session() as session:
                stmt = select(func.count(Viewing.id)).where(
                    Viewing.tg_user_id == tg_user_id
                )
                return int(session.scalar(stmt) or 0)
        except SQLAlchemyError as exc:
            raise RepositoryError("Не удалось получить количество посещений") from exc

    def get_by_id_for_user(
        self,
        viewing_id: int,
        tg_user_id: int,
    ) -> Viewing | None:
        try:
            with self.database.session() as session:
                stmt = select(Viewing).where(
                    Viewing.id == viewing_id,
                    Viewing.tg_user_id == tg_user_id,
                )
                return session.scalar(stmt)
        except SQLAlchemyError as exc:
            raise RepositoryError("Не удалось загрузить посещение") from exc

    def update_note(
        self,
        viewing_id: int,
        tg_user_id: int,
        note: str,
    ) -> Viewing | None:
        try:
            with self.database.session() as session:
                stmt = select(Viewing).where(
                    Viewing.id == viewing_id,
                    Viewing.tg_user_id == tg_user_id,
                )
                viewing = session.scalar(stmt)

                if viewing is None:
                    return None

                viewing.note = note
                session.commit()
                session.refresh(viewing)
                return viewing
        except SQLAlchemyError as exc:
            raise RepositoryError("Не удалось сохранить заметку") from exc
