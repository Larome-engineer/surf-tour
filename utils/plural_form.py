def get_plural_form(number: int, one: str, few: str, many: str) -> str:
    n = abs(number)
    if n % 10 == 1 and n % 100 != 11:
        return one
    elif 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return few
    else:
        return many
