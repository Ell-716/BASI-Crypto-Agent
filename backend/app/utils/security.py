"""
Security utilities for password and username validation.

Provides functions to enforce password strength requirements and validate
username format according to application security policies.
"""
import re
import string


def is_strong_password(password: str) -> bool:
    """
    Validate password strength.

    Password must contain:
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - At least one special character (any standard ASCII punctuation)
    - Minimum 8 characters

    Args:
        password: Password string to validate

    Returns:
        bool: True if password meets requirements, False otherwise
    """
    if len(password) < 8:
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    # Accept all standard ASCII special characters (string.punctuation):
    # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    if not any(c in string.punctuation for c in password):
        return False
    return True


def is_valid_username(username):
    """
    Validate username format.

    Username must contain only letters, numbers, and underscores,
    with a minimum length of 3 characters.

    Args:
        username: Username string to validate

    Returns:
        bool: True if username is valid, False otherwise
    """
    return re.match(r'^[a-zA-Z0-9_]{3,}$', username) is not None
