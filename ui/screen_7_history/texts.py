from models.viewing import Viewing


def get_screen_7_history_text(
    items: list[Viewing],
    page: int,
    total_pages: int,
) -> str:
    if not items:
        return (
            "История просмотров пока пуста.\n"
            "Сначала сохраните посещение кинотеатра."
        )

    lines = [
        f"История просмотров — страница {page + 1}/{total_pages}:\n"
    ]

    for index, viewing in enumerate(items, start=1):
        lines.append(
            f"{index}. {viewing.viewing_date.strftime('%d.%m.%Y')} — "
            f"{viewing.film_name}"
        )

    return "\n".join(lines)
