from functools import wraps

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
from .fields import (
    quote_fields,
    quotes_fields
)


def _admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            abort(403)

        return func(args, **kwargs)

    return wrapper


def _get_quote_args():
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('author', type=str, required=True, nullable=False)
    parser.add_argument('quotation', type=str, required=True, nullable=False)
    parser.add_argument('source', type=str)

    return parser.parse_args()


class Quotes(Resource):

    @marshal_with(quotes_fields)
    @jwt_optional
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()

        search_query = args['q']
        page = args['page']
        per_page = args['per_page']

        current_user = get_jwt_identity()
        user_id = current_user['id'] if current_user else None

        if search_query:
            return db_client.search_quotes(search_query, page, per_page, user_id)

        return db_client.get_quotes(page, per_page, user_id)

    @marshal_with(quote_fields)
    @jwt_required
    def post(self):
        args = _get_quote_args()

        current_user = get_jwt_identity()
        args['is_published'] = current_user['is_admin']

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

        return db_client.get_quote_or_404(quote_id, user_id)

    @marshal_with(quote_fields)
    @jwt_required
    @_admin_only
    def patch(self, quote_id):
        args = _get_quote_args()
        current_user = get_jwt_identity()
        quote = db_client.get_quote_or_404(quote_id, current_user['id'])

        return db_client.update_quote(quote, args)

    @jwt_required
    @_admin_only
    def delete(self, quote_id):
        current_user = get_jwt_identity()
        quote = db_client.get_quote_or_404(quote_id, current_user['id'])
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
