"""This module contains the likes API."""

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
    """Resource for likes."""

    @classmethod
    @marshal_with(quotes_fields)
    @jwt_required
    def get(cls):
        """Returns the liked quotes of the current user."""

        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, location='args')
        parser.add_argument('per_page', type=int, location='args')
        args = parser.parse_args()
        page = args['page']
        per_page = args['per_page']

        current_user = get_jwt_identity()
        return db_client.get_user_liked_quotes(page, per_page, current_user['id'])

    @classmethod
    @marshal_with(quote_fields)
    @jwt_required
    def post(cls):
        """Creates a like for the current user."""

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

        quote.is_liked = True
        return quote


class Like(Resource):
    """Resource for like."""

    @classmethod
    @marshal_with(quote_fields)
    @jwt_required
    def delete(cls, quote_id):
        """Deletes a like from the current user."""

        current_user = get_jwt_identity()
        quote = get_quote_or_404(quote_id, current_user['id'])

        try:
            like = db_client.get_like(current_user['id'], quote.id)
            db_client.delete_like(like)
        except AttributeError:
            return {'success': False}

        quote.is_liked = False
        return quote
