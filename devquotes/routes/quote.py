from flask_restful import (
    marshal_with,
    reqparse,
    Resource,
)

from .fields import quote_fields
from devquotes.models import db
from devquotes.models.quote import Quote


class QuoteList(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('author', type=str, required=True)
        self.parser.add_argument('quotation', type=str, required=True)
        self.parser.add_argument('source', type=str, required=False)

    @marshal_with(quote_fields)
    def post(self):
        args = self.parser.parse_args()

        quote = Quote()
        quote.author = args['author']
        quote.quotation = args['quotation']
        quote.source = args['source'].strip() \
            if args['source'].strip() else None

        db.session.add(quote)
        db.session.commit()

        return quote
