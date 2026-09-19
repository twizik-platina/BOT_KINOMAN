from models.movie import Movie


def get_screen_6_movies_text(
    cinema_name: str,
    date_text: str,
    movies: list[Movie],
) -> str:
    if not movies:
        return (
            f"На {date_text} для кинотеатра «{cinema_name}» "
            "фильмы не найдены."
        )

    lines = [
        f"Фильмы в прокате в «{cinema_name}» на {date_text}:\n"
    ]

    for index, movie in enumerate(movies, start=1):
        description = movie.description.strip()

        if len(description) > 250:
            description = description[:247].rstrip() + "..."

        lines.append(
            f"{index}. {movie.title}\n"
            f"{description}"
        )

    return "\n\n".join(lines)
