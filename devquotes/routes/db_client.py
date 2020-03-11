# pylint: disable=redefined-builtin
from flask import abort, current_app
from sqlalchemy import case

from devquotes.models.like import Like
from devquotes.models.user import User
from devquotes.models.quote import Quote


def _quote_base_query():
    case_stmt = case([(Like.id.isnot(None), True)], else_=False)
    return Quote.query.add_columns(case_stmt.label("is_liked"))


def _prepare_quote(*args):
    quote, is_liked = args
    quote.is_liked = is_liked
    return quote


def _paginate_quote(query, page, per_page):
    if per_page is None:
        per_page = current_app.config.get('QUOTES_PER_PAGE', 10)

    result = query.paginate(page, per_page, error_out=True)
    result.items = [_prepare_quote(*item) for item in result.items]
    return result


def get_quotes(page, per_page, user_id=None):
    query = _quote_base_query()\
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))\
        .order_by(Quote.created_at.desc())

    return _paginate_quote(query, page, per_page)


def get_user_liked_quotes(page, per_page, user_id=None):
    query = _quote_base_query()\
        .join(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))\
        .filter(Quote.likes > 0)\
        .order_by(Like.created_at.desc())

    return _paginate_quote(query, page, per_page)


def get_quote_or_404(quote_id, user_id=None):
    result = _quote_base_query()\
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))\
        .filter(Quote.id == quote_id)\
        .first()

    if result is None:
        abort(404)

    quote, like_id = result
    return _prepare_quote(quote, like_id)


def like_quote(quote):
    updated_quote = update_quote(quote, {'likes': quote.likes + 1})
    return _prepare_quote(updated_quote, True)


def unlike_quote(quote):
    updated_quote = update_quote(quote, {'likes': quote.likes - 1})
    return _prepare_quote(updated_quote, False)


def update_quote(quote, data):
    return quote.update(**data)


def create_quote(data):
    return Quote.create(**data)


def delete_quote(quote):
    likes = Like.get_by(first=False, quote_id=quote.id)
    for like in likes:
        delete_like(like)
    quote.delete()


def get_like(user_id, quote_id):
    return Like.get_by(first=True, user_id=user_id, quote_id=quote_id)


def create_like(data):
    Like.create(**data)


def delete_like(like):
    like.delete()


def get_user(firebase_user_id):
    return User.get_by(first=True, firebase_user_id=firebase_user_id)


def create_user(data):
    return User.create(**data)
