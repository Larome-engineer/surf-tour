import datetime

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}
def format_date_range(start: datetime.date, end: datetime.date) -> str:
    start_str = f"{start.day} {MONTHS_RU[start.month]}"
    end_str = f"{end.day} {MONTHS_RU[end.month]}"
    return f"{start_str} – {end_str}"
