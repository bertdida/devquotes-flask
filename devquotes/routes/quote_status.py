"""This module contains the quote statuses API."""

from flask_jwt_extended import jwt_required
from flask_restful import marshal_with, Resource

from . import db_client
from .fields import quotes_statuses_fields
from .utils import admin_only


class QuoteStatus(Resource):
    """Resource for quote statuses."""

    @classmethod
    @marshal_with(quotes_statuses_fields)
    @jwt_required
    @admin_only
    def get(cls):
        """Returns all quote statuses."""

        # https://github.com/flask-restful/flask-restful/issues/300
        return {'items': db_client.get_quote_statuses()}
