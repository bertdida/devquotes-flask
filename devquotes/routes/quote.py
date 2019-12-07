from flask_restful import (
    marshal_with,
    reqparse,
    Resource,
)

from .db_client import create_quote
from .fields import quote_fields


class QuoteList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('author', type=str, required=True)
        self.parser.add_argument('quotation', type=str, required=True)
        self.parser.add_argument('source', type=str, required=False)

    @marshal_with(quote_fields)
    def post(self):
        args = self.parser.parse_args()
        return create_quote({
            'author': args['author'],
            'quotation':  args['quotation'],
            'source': args['source'].strip() if args['source'].strip() else None
        })
