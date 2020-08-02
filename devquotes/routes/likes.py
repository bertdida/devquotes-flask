from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from flask_restful import (
    marshal_with,
    reqparse,
    Resource,
)
from sqlalchemy.exc import IntegrityError

from . import db_client
from .fields import quote_fields, quotes_fields
from .utils import get_quote_or_404


class Likes(Resource):

    @marshal_with(quotes_fields)
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        current_user = get_jwt_identity()
        return db_client.get_user_liked_quotes(page, per_page, current_user['id'])

    @marshal_with(quote_fields)
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        args = parser.parse_args()

        current_user = get_jwt_identity()
        quote = get_quote_or_404(args['id'], current_user['id'])

        try:
            db_client.create_like({
                'user_id': current_user['id'],
                'quote_id': quote.id
            })
        except IntegrityError:
            return {'success': False}

        return quote


class Like(Resource):

    @marshal_with(quote_fields)
    @jwt_required
    def delete(self, quote_id):
        current_user = get_jwt_identity()
        quote = get_quote_or_404(quote_id, current_user['id'])

        try:
            like = db_client.get_like(current_user['id'], quote.id)
            db_client.delete_like(like)
        except AttributeError:
            return {'success': False}

        return quote
