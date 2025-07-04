import re

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

def is_valid_phone(phone: str) -> bool:
    try:
        parsed = phonenumbers.parse(phone, "RU")  # RU — по умолчанию Россия
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False


from email_validator import validate_email, EmailNotValidError

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def is_valid_time(text):
    return bool(re.match(r'^\d{2}:\d{2}$', text))