import re


def is_strong_password(password: str) -> bool:
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return bool(re.match(pattern, password))


def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9_]{3,}$', username) is not None
