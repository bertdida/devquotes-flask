from flask_restful import (
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
            'source': args['source'].strip() if args['source'].strip() else None
        })
