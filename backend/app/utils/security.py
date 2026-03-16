"""
Security utilities for password and username validation.

Provides functions to enforce password strength requirements and validate
username format according to application security policies.
"""
import re


def is_strong_password(password: str) -> bool:
    """
    Validate password strength.

    Password must contain:
    - At least one lowercase letter
    - At least one uppercase letter
    - At least one digit
    - At least one special character (@$!%*?&)
    - Minimum 8 characters

    Args:
        password: Password string to validate

    Returns:
        bool: True if password meets requirements, False otherwise
    """
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return bool(re.match(pattern, password))


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
