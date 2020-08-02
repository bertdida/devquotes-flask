from functools import wraps

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from . import db_client


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            abort(403)

        return func(args, **kwargs)

    return wrapper


def get_quote_or_404(quote_id, user_id=None):
    quote = db_client.get_quote(quote_id, user_id)
    if quote is None:
        abort(404)

    return quote
