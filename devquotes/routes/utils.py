"""This module contains common functions used in the route controllers."""

from functools import wraps

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from . import db_client


def admin_only(func):
    """This decorator aborts with 403 if the current user is not an admin."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            abort(403)

        return func(args, **kwargs)

    return wrapper


def get_quote_or_404(quote_id, user_id=None):
    """Aborts with 404 if the quote with the given id is not found.

    Args:
        quote_id (int): The quote's id.
        user_id (int, optional): The user's id to determine if
            quote is liked or not. Defaults to None.

    Returns:
        object: The quote's model.
    """

    quote = db_client.get_quote(quote_id, user_id)
    if quote is None:
        abort(404)

    return quote
