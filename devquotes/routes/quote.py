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


def _non_empty_string(string):
    if not string:
        raise ValueError('Must not be an empty string')

    return string


class Quotes(Resource):

    @marshal_with(quotes_fields)
    @jwt_optional
    def get(self):
        statuses = db_client.get_quote_statuses()
        status_choices = [status.name for status in statuses]

        parser = reqparse.RequestParser()
        parser.add_argument('q', location='args')
        parser.add_argument('page', location='args', type=int)
        parser.add_argument('per_page', location='args', type=int)
        parser.add_argument('status', location='args', choices=status_choices)
        args = parser.parse_args()

        search_query = args['q']
        page = args['page']
        per_page = args['per_page']
        status = args['status']

        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        if search_query:
            return db_client.search_quotes(search_query, page, per_page, user_id)

        return db_client.get_quotes(page, per_page, user_id, status)

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

        status = args.pop('status', 'pending_review')
        if status:
            for curr_status in statuses:
                if curr_status.name == status:
                    args['status'] = curr_status

        try:
            return db_client.create_quote(args), 201
        except IntegrityError:
            abort(409)


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
