from datetime import date, datetime

DAYS_RU = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Вс"
}

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}


def format_date_range(start: datetime.date, end: datetime.date) -> str:
    start_str = f"{start.day} {MONTHS_RU[start.month]}"
    end_str = f"{end.day} {MONTHS_RU[end.month]}"
    return f"{start_str} – {end_str}"


def parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return None


def perform_date(lesson_date: datetime | str, lesson_time: str) -> str:
    if isinstance(lesson_date, str):
        lesson_date = parse_date(lesson_date)
    return (
        f"{DAYS_RU[lesson_date.weekday()]}, {lesson_date.day} "
        f"{MONTHS_RU[lesson_date.month]} | {lesson_time}"
    )
