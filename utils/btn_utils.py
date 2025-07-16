from datetime import date

from utils.date_utils import MONTHS_RU, DAYS_RU


def btn_perform(type_of: str, start: date, time: str, is_lesson: bool = True, end_date = None) -> str:
    if is_lesson:
        lsn_type = type_of.split(" ")
        about = f"{lsn_type[0][:5]}.{lsn_type[1]}"
        return (
            f"{about} |"
            f"{DAYS_RU[start.weekday()]}, {start.day} {MONTHS_RU[start.month]} | "
            f"{time}"
        )
    else:
        return f"{type_of} | {start} - {end_date} | {time}"


