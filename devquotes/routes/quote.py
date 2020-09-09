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


def _non_empty_string(string):
    if not string:
        raise ValueError('Must not be an empty string')

    return string


def _valid_likes_pattern(string):
    if not LIKES_FILTER_RE.match(string):
        pattern = LIKES_FILTER_RE.pattern
        raise ValueError(f'Invalid pattern, must follow {pattern}')

    return string


def _ids(string):
    ids = set(string.split(','))

    if not all(i.isdigit() for i in ids):
        raise ValueError('Invalid type, each id must be type of integer')

    if len(ids) > TOTAL_ALLOWED_IDS:
        raise ValueError(
            f'A total of {TOTAL_ALLOWED_IDS} '
            f'{"ids are" if TOTAL_ALLOWED_IDS > 1 else "id is"} allowed'
        )

    return string


class Quotes(Resource):

    @marshal_with(quotes_fields)
    @jwt_optional
    def get(self):
        statuses = db_client.get_quote_statuses()
        status_choices = [status.name for status in statuses]

        parser = reqparse.RequestParser()
        parser.add_argument('query', location='args')
        parser.add_argument('page', location='args', type=int)
        parser.add_argument('per_page', location='args', type=int)
        parser.add_argument('status', location='args', choices=status_choices)
        parser.add_argument('submitted_by', location='args')
        parser.add_argument('likes', location='args', type=_valid_likes_pattern)  # noqa
        args = parser.parse_args()

        search_query = args['query']
        page = args['page']
        per_page = args['per_page']
        status = args['status']
        submitted_by = args['submitted_by']
        likes = args['likes']

        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        if search_query:
            return db_client.search_quotes(search_query, page, per_page, user_id)

        filters = {
            'status': status,
            'submitted_by': submitted_by,
            'likes': likes,
        }

        return db_client.get_quotes(page, per_page, user_id, **filters)

    @marshal_with(quote_fields)
    @jwt_required
    def post(self):
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

        status_fallback = 'published' if current_user['is_admin'] else 'pending_review'
        status = args.pop('status', status_fallback)

        if status:
            for curr_status in statuses:
                if curr_status.name == status:
                    args['status'] = curr_status

        try:
            return db_client.create_quote(args), 201
        except IntegrityError:
            abort(409)

    @jwt_required
    @admin_only
    def delete(self):
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

            results.append({'id': quote_id, 'success': success})

        return results


class Quote(Resource):

    @marshal_with(quote_fields)
    @jwt_optional
    def get(self, quote_id):
        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        return get_quote_or_404(quote_id, user_id)

    @marshal_with(quote_fields)
    @jwt_required
    @admin_only
    def patch(self, quote_id):
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

    @jwt_required
    @admin_only
    def delete(self, quote_id):
        current_user = get_jwt_identity()
        quote = get_quote_or_404(quote_id, current_user['id'])
        db_client.delete_quote(quote)

        return '', 204


class Random(Resource):

    @marshal_with(quote_fields)
    @jwt_optional
    def get(self):
        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        quote = db_client.get_random_quote(user_id)
        if quote is None:
            abort(404)

        return quote


class Contributor(Resource):

    @marshal_with(user_fields)
    @jwt_required
    @admin_only
    def get(self, quote_id):
        quote = get_quote_or_404(quote_id)
        return quote.contributor
