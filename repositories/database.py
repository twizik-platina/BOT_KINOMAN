from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


class DatabaseError(Exception):
    pass


class Database:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.session_factory = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def check_connection(self) -> None:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Не удалось подключиться к PostgreSQL. "
                "Проверьте DATABASE_URL и запущен ли PostgreSQL."
            ) from exc

    def create_tables(self) -> None:
        # Импорт нужен, чтобы SQLAlchemy зарегистрировал модель Viewing.
        from models.viewing import Viewing  # noqa: F401

        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as exc:
            raise DatabaseError("Не удалось создать таблицы PostgreSQL") from exc

    def session(self):
        return self.session_factory()
