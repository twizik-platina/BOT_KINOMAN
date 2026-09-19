from models.movie import Movie


def get_screen_3_premieres_text(movies: list[Movie]) -> str:
    if not movies:
        return "Премьер на ближайшие 7 дней не найдено."

    lines = ["Премьеры фильмов на ближайшие 7 дней:\n"]

    for index, movie in enumerate(movies, start=1):
        premiere = ""

        if movie.premiere_date is not None:
            premiere = f" — {movie.premiere_date.strftime('%d.%m.%Y')}"

        description = movie.description.strip()

        if len(description) > 300:
            description = description[:297].rstrip() + "..."

        lines.append(
            f"{index}. {movie.title}{premiere}\n"
            f"{description}"
        )

    return "\n\n".join(lines)
