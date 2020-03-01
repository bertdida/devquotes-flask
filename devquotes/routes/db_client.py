# pylint: disable=redefined-builtin
from flask import current_app

from devquotes.models.like import Like
from devquotes.models.user import User
from devquotes.models.quote import Quote


def _paginate(query, page, per_page):
    if per_page is None:
        per_page = current_app.config.get('QUOTES_PER_PAGE', 10)

    return query.paginate(page, per_page, error_out=True)


def get_user(firebase_user_id):
    return User.get_by(first=True, firebase_user_id=firebase_user_id)


def create_user(data):
    return User.create(**data)


def create_quote(data):
    return Quote.create(**data)


def get_quotes(page, per_page):
    query = Quote.query.order_by(Quote.created_at.desc())
    return _paginate(query, page, per_page)


def get_quote(id):
    return Quote.get(id)


def get_quote_or_404(id):
    return Quote.get_or_404(id)


def update_quote(quote, data):
    return quote.update(**data)


def delete_quote(quote):
    quote.delete()


def get_like(user_id, quote_id):
    return Like.get_by(first=True, user_id=user_id, quote_id=quote_id)


def create_like(data):
    Like.create(**data)


def delete_like(like):
    like.delete()


def like_quote(quote):
    return update_quote(quote, {'likes': quote.likes + 1})


def unlike_quote(quote):
    return update_quote(quote, {'likes': quote.likes - 1})


def get_user_liked_quotes(user_id, page, per_page):
    query = Quote.query.join(Like, Quote.id == Like.quote_id)\
        .join(User, Like.user_id == user_id)\
        .order_by(Like.created_at.desc())
    return _paginate(query, page, per_page)
