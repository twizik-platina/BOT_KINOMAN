from models.cinema import Cinema


DATE_PROMPT = (
    "Введите дату сеанса в формате ДД.ММ.ГГГГ."
)


def get_screen_5_cinemas_text(cinemas: list[Cinema]) -> str:
    if not cinemas:
        return "Кинотеатры для выбранного города не найдены."

    lines = ["Кинотеатры с актуальными сеансами:\n"]

    for index, cinema in enumerate(cinemas, start=1):
        lines.append(
            f"{index}. {cinema.title}\n"
            f"{cinema.address}"
        )

    return "\n\n".join(lines)
