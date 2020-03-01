# pylint: disable=redefined-builtin
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


def _non_empty_string(value):
    if not value:
        raise ValueError("Must not be an empty string")
    return value


def _get_quote_reqparser():
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument(
        'author',
        type=_non_empty_string,
        required=True,
        nullable=False
    )
    parser.add_argument(
        'quotation',
        type=_non_empty_string,
        required=True,
        nullable=False
    )
    parser.add_argument(
        'source',
        type=_non_empty_string,
        nullable=False
    )

    return parser.parse_args()


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
        args = _get_quote_reqparser()
        return db_client.create_quote(args), 201


class Quote(Resource):

    @marshal_with(quote_fields)
    @jwt_optional
    def get(self, id):
        return db_client.get_quote_or_404(id)

    @marshal_with(quote_fields)
    @jwt_required
    def patch(self, id):
        quote = db_client.get_quote_or_404(id)

        current_user = get_jwt_identity()
        if not current_user['is_admin']:
            abort(403)

        args = _get_quote_reqparser()
        return db_client.update_quote(quote, args)

    def delete(self, id):
        quote = db_client.get_quote_or_404(id)
        db_client.delete_quote(quote)
        return '', 204
