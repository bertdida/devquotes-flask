"""This module contains the quotes API."""

import re

from flask_jwt_extended import (
    get_jwt_identity,
    jwt_optional,
    jwt_required,
)
from flask_restful import (
    abort,
    marshal_with,
    reqparse,
    Resource,
)
from sqlalchemy.exc import IntegrityError

from . import db_client
from .fields import quote_fields, quotes_fields, user_fields
from .utils import admin_only, get_quote_or_404

LIKES_FILTER_RE = re.compile(r'^(?P<operator>[g|l|e]t)(?P<value>\d*)$')
TOTAL_ALLOWED_IDS = 50


class Quotes(Resource):
    """Resource for quotes."""

    @classmethod
    @marshal_with(quotes_fields)
    @jwt_optional
    def get(cls):
        """Returns quotes with regards to the given query parameters."""

        # pylint: disable=too-many-locals

        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None
        is_not_admin = not user_id or not current_user['is_admin']

        status_choices = []
        if not is_not_admin:
            statuses = db_client.get_quote_statuses()
            status_choices = [status.name for status in statuses]

        parser = reqparse.RequestParser()
        parser.add_argument('query', location='args')
        parser.add_argument('page', location='args', type=int)
        parser.add_argument('per_page', location='args', type=int)
        parser.add_argument('status', location='args', choices=status_choices)
        parser.add_argument('submitted_by', location='args')
        parser.add_argument(
            'likes', location='args', type=_valid_likes_pattern
        )
        args = parser.parse_args()

        search_query = args['query']
        page = args['page']
        per_page = args['per_page']
        status = args['status']
        likes = args['likes']
        submitted_by = args['submitted_by']

        restricted_args = ['status', 'likes', 'submitted_by']
        if is_not_admin and any(args[a] for a in restricted_args):
            # non-admin users are not allowed to set value on any of the
            # restricted arguments
            abort(403)

        if search_query:
            return db_client.search_quotes(search_query, page, per_page, user_id)

        filters = {
            'status': status,
            'submitted_by': submitted_by,
            'likes': likes,
        }

        return db_client.get_quotes(page, per_page, user_id, **filters)

    @classmethod
    @marshal_with(quote_fields)
    @jwt_required
    def post(cls):
        """Creates quote."""

        statuses = db_client.get_quote_statuses()
        status_choices = [status.name for status in statuses]

        parser = reqparse.RequestParser(trim=True)
        parser.add_argument(
            'author',
            location=('json', 'form'),
            nullable=False,
            required=True,
            type=_non_empty_string,
        )
        parser.add_argument(
            'quotation',
            location=('json', 'form'),
            nullable=False,
            required=True,
            type=_non_empty_string,
        )
        parser.add_argument(
            'source',
            location=('json', 'form'),
            nullable=True,
            type=_non_empty_string,
        )
        parser.add_argument(
            'status',
            location=('json', 'form'),
            nullable=False,
            store_missing=False,
            choices=status_choices,
        )
        args = parser.parse_args()

        current_user = get_jwt_identity()
        args['contributor_id'] = current_user['id']

        status = args.pop('status', 'pending_review') \
            if current_user['is_admin'] else 'pending_review'

        if status:
            for curr_status in statuses:
                if curr_status.name == status:
                    args['status'] = curr_status

        try:
            return db_client.create_quote(args), 201
        except IntegrityError:
            abort(409)

    @classmethod
    @jwt_required
    @admin_only
    def delete(cls):
        """Deletes quote."""

        parser = reqparse.RequestParser()
        parser.add_argument('ids', location='args', type=_ids)
        args = parser.parse_args()

        ids = args['ids']
        results = []

        for quote_id in ids.split(','):
            quote = db_client.get_quote(quote_id)
            success = False

            if quote:
                success = True
                db_client.delete_quote(quote)

            results.append({'id': int(quote_id), 'success': success})

        return results


class Quote(Resource):
    """Resource for quote."""

    @classmethod
    @marshal_with(quote_fields)
    @jwt_optional
    def get(cls, quote_id):
        """Returns quote by id."""

        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        return get_quote_or_404(quote_id, user_id)

    @classmethod
    @marshal_with(quote_fields)
    @jwt_required
    @admin_only
    def patch(cls, quote_id):
        """Updates quote by id."""

        statuses = db_client.get_quote_statuses()
        status_choices = [status.name for status in statuses]

        parser = reqparse.RequestParser(trim=True)
        parser.add_argument(
            'author',
            location=('json', 'form'),
            nullable=False,
            store_missing=False,
            type=_non_empty_string,
        )
        parser.add_argument(
            'quotation',
            location=('json', 'form'),
            nullable=False,
            store_missing=False,
            type=_non_empty_string,
        )
        parser.add_argument(
            'source',
            location=('json', 'form'),
            nullable=True,
            store_missing=False,
            type=_non_empty_string,
        )
        parser.add_argument(
            'status',
            location=('json', 'form'),
            nullable=False,
            store_missing=False,
            choices=status_choices,
        )
        args = parser.parse_args()

        status = args.pop('status', None)
        if status:
            for curr_status in statuses:
                if curr_status.name == status:
                    args['status'] = curr_status

        current_user = get_jwt_identity()
        quote = get_quote_or_404(quote_id, current_user['id'])

        return db_client.update_quote(quote, args)

    @classmethod
    @jwt_required
    @admin_only
    def delete(cls, quote_id):
        """Deletes quote by id."""

        current_user = get_jwt_identity()
        quote = get_quote_or_404(quote_id, current_user['id'])
        db_client.delete_quote(quote)

        return '', 204


class Random(Resource):
    """Resource for random quote."""

    @classmethod
    @marshal_with(quote_fields)
    @jwt_optional
    def get(cls):
        """Returns a random quote."""

        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        quote = db_client.get_random_quote(user_id)
        if quote is None:
            abort(404)

        return quote


class Contributor(Resource):
    """Resource for quote's contributor."""

    @classmethod
    @marshal_with(user_fields)
    @jwt_required
    @admin_only
    def get(cls, quote_id):
        """Returns the contributor of the given quote id."""

        quote = get_quote_or_404(quote_id)
        return quote.contributor


def _non_empty_string(string):
    """A helper to check if the given string is empty.

    Args:
        string (string): The string to check.

    Raises:
        ValueError: This will be raised if the string is empty.

    Returns:
        string: The string.
    """

    if not string:
        raise ValueError('Must not be an empty string')

    return string


def _valid_likes_pattern(string):
    """A helper to check if the given string is a valid like query pattern.

    Args:
        string (string): The string to check.

    Raises:
        ValueError: This will be raised if the string is an invalid pattern.

    Returns:
        string: The string.
    """

    if not LIKES_FILTER_RE.match(string):
        pattern = LIKES_FILTER_RE.pattern
        raise ValueError(f'Invalid pattern, must follow {pattern}')

    return string


def _ids(string):
    """A helper to check if the given comma-separated ids are all integer
    and does not exceed the allowed total ids.

    Args:
        string (string): The string to check.

    Raises:
        ValueError: This will be raised with an appropriate message.

    Returns:
        string: The string.
    """

    ids = set(string.split(','))

    if not all(i.isdigit() for i in ids):
        raise ValueError('Invalid type, each id must be type of integer')

    if len(ids) > TOTAL_ALLOWED_IDS:
        raise ValueError(
            f'A total of {TOTAL_ALLOWED_IDS} '
            f'{"ids are" if TOTAL_ALLOWED_IDS > 1 else "id is"} allowed'
        )

    return string
