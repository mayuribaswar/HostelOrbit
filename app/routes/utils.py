from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("You are not authorized for this section.", "danger")
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def parse_int(value, default=None, min_value=None, max_value=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if min_value is not None and parsed < min_value:
        return default
    if max_value is not None and parsed > max_value:
        return default
    return parsed


def parse_float(value, default=None, min_value=None):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if min_value is not None and parsed < min_value:
        return default
    return parsed
