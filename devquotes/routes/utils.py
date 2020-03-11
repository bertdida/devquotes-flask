from functools import wraps

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            abort(403)

        return func(args, **kwargs)

    return wrapper


def _set_attributes(obj, **kwargs):
    for key, value in kwargs.items():
        setattr(obj, key, value)

    return obj
