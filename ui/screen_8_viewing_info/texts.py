from models.viewing import Viewing


def get_screen_8_viewing_text(viewing: Viewing) -> str:
    note = viewing.note or "Заметка отсутствует."

    return (
        "Информация о посещении\n\n"
        f"Дата: {viewing.viewing_date.strftime('%d.%m.%Y')}\n"
        f"Город: {viewing.city}\n"
        f"Кинотеатр: {viewing.cinema}\n"
        f"Фильм: {viewing.film_name}\n\n"
        f"Заметка:\n{note}"
    )
