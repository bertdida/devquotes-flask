import operator as op

from flask import current_app
from sqlalchemy import and_, case, event
from sqlalchemy.sql.expression import func

from devquotes.models.like import Like
from devquotes.models.user import User
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus

PUBLISHED_STATUS_NAME = 'published'


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


def _parse_likes_filter(value):
    from .quote import LIKES_FILTER_RE

    operator_map = {
        'gt': op.gt,
        'et': op.eq,
        'lt': op.lt,
    }

    match = LIKES_FILTER_RE.search(value)
    operator = match.group('operator')
    value = match.group('value')

    return operator_map[operator], int(value)


def _get_filter_queries(**filters):
    filter_configs = {
        'status': {
            'model': QuoteStatus,
            'attribute': 'name',
            'value': PUBLISHED_STATUS_NAME,
        },
        'submitted_by': {
            'model': User,
            'attribute': 'name',
            'value': None,
        },
        'likes': {
            'model': Quote,
            'attribute': 'total_likes',
            'value': None,
        }
    }

    queries = []
    filter_configs_keys = filter_configs.keys()

    # override `filter_configs` values from the given filters
    for key, value in filters.items():
        if value and key in filter_configs_keys:
            filter_configs[key]['value'] = value

    for key, config in filter_configs.items():
        operator = op.eq
        value = config['value']
        model = config['model']
        attribute = config['attribute']

        if not value:
            continue

        if key == 'likes':
            operator, value = _parse_likes_filter(value)

        query = operator(getattr(model, attribute), value)
        queries.append(query)

    return queries


def get_quotes(page, per_page, user_id=None, **filters):
    filter_queries = _get_filter_queries(**filters)

    query = (
        Quote.query
        .join(User)
        .join(QuoteStatus)
        .filter(and_(*filter_queries))
        .add_columns(case([(Like.quote_id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .order_by(Quote.created_at.desc())
    )

    return _paginate_quote(query, page, per_page)


def search_quotes(search_query, page, per_page, user_id=None):
    query = (
        Quote.query
        .join(QuoteStatus)
        .filter(QuoteStatus.name == PUBLISHED_STATUS_NAME)
        .add_columns(case([(Like.quote_id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .search(search_query, sort=True)
    )

    return _paginate_quote(query, page, per_page)


def get_user_liked_quotes(page, per_page, user_id=None):
    query = (
        Quote.query
        .join(QuoteStatus)
        .filter(QuoteStatus.name == PUBLISHED_STATUS_NAME)
        .add_columns(case([(Like.quote_id.isnot(None), True)], else_=False).label('is_liked'))
        .join(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(Quote.total_likes > 0)
        .order_by(Like.created_at.desc())
    )

    return _paginate_quote(query, page, per_page)


def get_quote(quote_id, user_id=None):
    result = (
        Quote.query
        .add_columns(case([(Like.quote_id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .filter(Quote.id == quote_id)
        .first()
    )

    if result is None:
        return None

    quote, is_liked = result
    return _set_attributes(quote, is_liked=is_liked)


def get_random_quote(user_id=None):
    result = (
        Quote.query
        .join(QuoteStatus)
        .filter(QuoteStatus.name == 'published')
        .add_columns(case([(Like.quote_id.isnot(None), True)], else_=False).label('is_liked'))
        .outerjoin(Like, (Like.quote_id == Quote.id) & (Like.user_id == user_id))
        .order_by(func.random())
        .first()
    )

    if result is None:
        return None

    quote, is_liked = result
    return _set_attributes(quote, is_liked=is_liked)


def update_quote(quote, data):
    return quote.update(**data)


def create_quote(data):
    return Quote.create(**data)


def delete_quote(quote):
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


def get_user_by_id(user_id):
    return User.get_by(first=True, id=user_id)


def get_quote_statuses():
    return QuoteStatus.query.all()


@event.listens_for(Like, 'after_insert')
def increment_quote_likes(_, connection, target):
    quote_table = Quote.__table__
    connection.execute(
        quote_table
        .update(Quote.id == target.quote_id)
        .values(total_likes=Quote.total_likes + 1)
    )


@event.listens_for(Like, 'after_delete')
def decrement_quote_likes(_, connection, target):
    quote_table = Quote.__table__
    connection.execute(
        quote_table
        .update(and_(Quote.id == target.quote_id, Quote.total_likes > 0))
        .values(total_likes=Quote.total_likes - 1)
    )
