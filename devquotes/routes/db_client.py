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


def get_quote(id):  # pylint: disable=redefined-builtin
    return Quote.get(id)


def update_quote(quote, data):
    return quote.update(**data)


def delete_quote(quote):
    quote.delete()


def is_liked(user_id, quote_id):
    like = Like.get_by(first=True, user_id=user_id, quote_id=quote_id)
    if not like:
        return False

    return True


def toggle_like(user_id, quote):
    like = Like.get_by(first=True, user_id=user_id, quote_id=quote.id)
    if not like:
        Like.create(user_id=user_id, quote_id=quote.id)
        quote.likes += 1
    else:
        like.delete()
        quote.likes -= 1

    return update_quote(quote, {'likes': quote.likes})
