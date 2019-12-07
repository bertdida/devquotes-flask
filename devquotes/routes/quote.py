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

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, location='args')
        self.parser.add_argument('per_page', type=int, location='args')

        self.parser.add_argument('author', type=str, required=True)
        self.parser.add_argument('quotation', type=str, required=True)
        self.parser.add_argument('source', type=str, required=False)

    @marshal_with(quotes_fields)
    def get(self):
        args = self.parser.parse_args()
        return db_client.get_quotes(args['page'], args['per_page'])

    @marshal_with(quote_fields)
    def post(self):
        args = self.parser.parse_args()
        return db_client.create_quote({
            'author': args['author'],
            'quotation':  args['quotation'],
            'source': args['source'].strip() if args['source'] else None
        }), 201


class Quote(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('author', type=str, required=True)
        self.parser.add_argument('quotation', type=str, required=True)
        self.parser.add_argument('source', type=str, required=False)
        self.parser.add_argument('likes', type=int, required=False)

    @marshal_with(quote_fields)
    def get(self, id):  # pylint: disable=redefined-builtin
        quote = db_client.get_quote(id)
        if not quote:
            abort(404)

        return quote

    @marshal_with(quote_fields)
    def patch(self, id):  # pylint: disable=redefined-builtin
        quote = db_client.get_quote(id)
        if not quote:
            abort(404)

        args = self.parser.parse_args()
        return db_client.update_quote(quote, {
            'author': args['author'],
            'quotation': args['quotation'],
            'source': args['source'].strip() if args['source'].strip() else None,
            'likes': args['likes'] if args['likes'] else quote.likes,
        })

    def delete(self, id):  # pylint: disable=redefined-builtin
        quote = db_client.get_quote(id)
        if not quote:
            abort(404)

        db_client.delete_quote(quote)
        return '', 204
