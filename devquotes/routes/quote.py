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

from . import db_client
from .fields import (
    quote_fields,
    quotes_fields
)


class QuoteList(Resource):

    @marshal_with(quotes_fields)
    @jwt_optional
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        return db_client.get_quotes(page, per_page)

    @marshal_with(quote_fields)
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser(trim=True)
        parser.add_argument('author', type=str, required=True)
        parser.add_argument('quotation', type=str, required=True)
        parser.add_argument('source', type=str)
        args = parser.parse_args()

        return db_client.create_quote(args), 201


class Quote(Resource):

    @marshal_with(quote_fields)
    @jwt_optional
    def get(self, id):  # pylint: disable=redefined-builtin
        quote = db_client.get_quote(id)
        if not quote:
            abort(404)

        return quote

    @marshal_with(quote_fields)
    @jwt_required
    def patch(self, id):  # pylint: disable=redefined-builtin
        quote = db_client.get_quote(id)
        if not quote:
            abort(404)

        parser = reqparse.RequestParser(trim=True)
        parser.add_argument('author', type=str, store_missing=False)
        parser.add_argument('quotation', type=str, store_missing=False)
        parser.add_argument('source', type=str, store_missing=False)
        parser.add_argument('is_liked', type=bool)
        args = parser.parse_args()
        current_user = get_jwt_identity()

        if args.pop('is_liked', None) is not None:
            return db_client.toggle_quote_like(current_user['id'], quote)

        if not current_user['is_admin']:
            abort(403)

        return db_client.update_quote(quote, args)

    def delete(self, id):  # pylint: disable=redefined-builtin
        quote = db_client.get_quote(id)
        if not quote:
            abort(404)

        db_client.delete_quote(quote)
        return '', 204
