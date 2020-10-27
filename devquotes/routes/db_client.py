"""This module contains all database operations used on the API endpoints."""

import operator as op

from flask import current_app
from sqlalchemy import and_, case, event
from sqlalchemy.sql.expression import func

from devquotes.models.like import Like
from devquotes.models.user import User
from devquotes.models.quote import Quote
from devquotes.models.quote_status import QuoteStatus

PUBLISHED_STATUS_NAME = current_app.config['PUBLISHED_STATUS_NAME']


def get_quotes(page, per_page, user_id=None, **filters):
    """Returns paginated quotes, most recent first.

    Args:
        page (int): The page of the results to return.
        per_page (int): The total records to return on the page.
        user_id (int, optional): The user's id to determine if
            quotes are liked or not. Defaults to None.
        filters (dict, optional): Filters to use in the query.

    Returns:
        object: The `flask_sqlalchemy.Pagination` results for `Quote` model.
    """

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
    """Returns quotes that matches the given query.

    Args:
        search_query (string): The query to use.
        page (int): The page of the results to return.
        per_page (int): The total records to return on the page.
        user_id (int, optional): The user's id to determine if
            quotes are liked or not. Defaults to None.

    Returns:
        object: The `flask_sqlalchemy.Pagination` results for `Quote` model.
    """

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
    """Returns user liked quotes.

    Args:
        page (int): The page of the results to return.
        per_page (int): The total records to return on the page.
        user_id (int, optional): The user's id. Defaults to None.

    Returns:
        object: The `flask_sqlalchemy.Pagination` results for `Quote` model.
    """

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
    """Returns quote by id.

    Args:
        quote_id (int): The quote's id.
        user_id (int, optional): The user's id to determine if
            quote is liked or not. Defaults to None.

    Returns:
        object: The quote's model.
    """

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
    """Returns random published quote.

    Args:
        user_id (int, optional): The user's id to determine if
            quote is liked or not. Defaults to None.

    Returns:
        object: The random quote's model.
    """

    result = (
        Quote.query
        .join(QuoteStatus)
        .filter(QuoteStatus.name == PUBLISHED_STATUS_NAME)
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
    """Updates quote.

    Args:
        quote (object): The Quote object to update.
        data (dict): The new data for the given quote.

    Returns:
        object: The updated quote's model.
    """

    return quote.update(**data)


def create_quote(data):
    """Creates quote.

    Args:
        data (dict): Then data of the quote that will be created.

    Returns:
        object: The created quote's model.
    """

    return Quote.create(**data)


def delete_quote(quote):
    """Deletes quote.

    Args:
        quote (object): The quote to be deleted.
    """

    quote.delete()


def get_like(user_id, quote_id):
    """Returns the like for the given user and quote id.

    Args:
        user_id (int): The user's id.
        quote_id (int): The quote's id.

    Returns:
        object: The like's model.
    """

    return Like.get_by(first=True, user_id=user_id, quote_id=quote_id)


def create_like(data):
    """Creates like.

    Args:
        data (dict): Then data of the like that will be created.

    Returns:
        object: The created like's model.
    """

    Like.create(**data)


def delete_like(like):
    """Deletes like.

    Args:
        like (object): The like to be deleted.
    """

    like.delete()


def get_user(firebase_user_id):
    """Returns user by `firebase_user_id`

    Args:
        firebase_user_id (string): The firebase user id saved on the table.

    Returns:
        object: The user's model.
    """

    return User.get_by(first=True, firebase_user_id=firebase_user_id)


def create_user(data):
    """Creates user.

    Args:
        data (dict): Then data of the user that will be created.

    Returns:
        object: The created user's model.
    """

    return User.create(**data)


def get_user_by_id(user_id):
    """Returns user by id.

    Args:
        user_id (int): The user's id.

    Returns:
        object: The user's model.
    """

    return User.get(model_id=user_id)


def get_quote_statuses():
    """Returns all quote statuses.

    Returns:
        list: The list of quote statuses' model.
    """

    return QuoteStatus.query.all()


def _get_filter_queries(**filters):
    """Returns a list of query expressions for the given `filters`."""

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


def _parse_likes_filter(string):
    """Parses a string and returns the like filter's operator and value.

    Args:
        string (string): The string to parse.

    Returns:
        tuple: The operator and the integer value.
    """

    # pylint: disable=import-outside-toplevel
    from .quote import LIKES_FILTER_RE

    operator_map = {
        'gt': op.gt,  # greater than
        'et': op.eq,  # equal to
        'lt': op.lt,  # less than
    }

    match = LIKES_FILTER_RE.search(string)
    operator = match.group('operator')
    value = match.group('value')

    return operator_map[operator], int(value)


def _paginate_quote(query, page, per_page):
    """A helper for paginating quote query.

    Args:
        query (object): The quote models `SearchQuery`.
        page (int): The page of the results to return.
        per_page (int): The total records to return on the page.

    Returns:
        object: The `flask_sqlalchemy.Pagination` results for `Quote` model.

    """

    if per_page is None:
        per_page = current_app.config.get('QUOTES_PER_PAGE', 10)

    result = query.paginate(page, per_page, error_out=True)
    result.items = [
        _set_attributes(quote, is_liked=is_liked) for quote, is_liked in result.items
    ]

    return result


def _set_attributes(obj, **kwargs):
    """Adds the `kwargs` as attribute to the given object."""

    for key, value in kwargs.items():
        setattr(obj, key, value)

    return obj


@event.listens_for(Like, 'after_insert')
def increment_quote_likes(_, connection, target):
    """An event listener that increments quote's `total_like`
    when like is created."""

    quote_table = Quote.__table__
    connection.execute(
        quote_table
        .update(Quote.id == target.quote_id)
        .values(total_likes=Quote.total_likes + 1)
    )


@event.listens_for(Like, 'after_delete')
def decrement_quote_likes(_, connection, target):
    """An event listener that decrements quote's `total_like`
    when like is deleted."""

    quote_table = Quote.__table__
    connection.execute(
        quote_table
        .update(and_(Quote.id == target.quote_id, Quote.total_likes > 0))
        .values(total_likes=Quote.total_likes - 1)
    )
