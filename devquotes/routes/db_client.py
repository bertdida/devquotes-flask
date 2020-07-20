from flask import current_app
from flask_restful import abort
from sqlalchemy import case, or_
from sqlalchemy.sql.expression import func

from devquotes.models.like import Like
from devquotes.models.user import User
from devquotes.models.quote import Quote


def _set_attributes(obj, **kwargs):
    for key, value in kwargs.items():
        setattr(obj, key, value)

    return obj


def _paginate_quote(query, page, per_page):
    if per_page is None:
        per_page = current_app.config.get('QUOTES_PER_PAGE', 10)

    result = query.paginate(page, per_page, error_out=True)
    result.items = [
        _set_attributes(quote, is_liked=is_liked) for quote, is_liked in result.items
    ]

    return result


def get_quotes(page, per_page, user_id=None, is_published=True):
    is_published_query = [Quote.is_published == is_published]
    if not is_published:
        is_published_query.append(Quote.is_published.is_(None))

    query = (
        Quote.query
        .add_columns(case([(Like.id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(or_(*is_published_query))
        .order_by(Quote.created_at.desc())
    )

    return _paginate_quote(query, page, per_page)


def search_quotes(search_query, page, per_page, user_id=None):
    query = (
        Quote.query
        .add_columns(case([(Like.id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(Quote.is_published)
        .search(search_query, sort=True)
    )

    return _paginate_quote(query, page, per_page)


def get_user_liked_quotes(page, per_page, user_id=None):
    query = (
        Quote.query
        .add_columns(case([(Like.id.isnot(None), True)], else_=False).label('is_liked'))
        .join(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(Quote.likes > 0, Quote.is_published)
        .order_by(Like.created_at.desc())
    )

    return _paginate_quote(query, page, per_page)


def get_quote_or_404(quote_id, user_id=None):
    result = (
        Quote.query
        .add_columns(case([(Like.id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(Quote.id == quote_id)
        .first()
    )

    if result is None:
        abort(404)

    quote, is_liked = result
    return _set_attributes(quote, is_liked=is_liked)


def get_random_quote(user_id=None):
    result = (
        Quote.query
        .add_columns(case([(Like.id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(Quote.is_published)
        .order_by(func.random()).first()
    )

    if result is None:
        return None

    quote, is_liked = result
    return _set_attributes(quote, is_liked=is_liked)


def like_quote(quote):
    updated_quote = update_quote(quote, {'likes': quote.likes + 1})
    return _set_attributes(updated_quote, is_liked=True)


def unlike_quote(quote):
    updated_quote = update_quote(quote, {'likes': quote.likes - 1})
    return _set_attributes(updated_quote, is_liked=False)


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


def get_user_or_404(user_id):
    result = User.get_by(first=True, id=user_id)

    if result is None:
        abort(404)

    return result
