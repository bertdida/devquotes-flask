from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import fields

from . import db_client


class PaginationUrl(fields.Raw):
    def format(self, value):
        if value is None:
            return None

        return '{}?page={}'.format(request.path, value)


class IsQuoteLikedByCurrentUser(fields.Raw):
    def format(self, quote_id):
        current_user = get_jwt_identity()
        if not current_user:
            return False

        return db_client.get_like(current_user['id'], quote_id) is not None


user_fields = {
    'data': {
        'is_admin': fields.Boolean,
    }
}

quote_fields = {
    'data': {
        'id': fields.Integer,
        'author': fields.String,
        'quotation': fields.String,
        'source': fields.String,
        'likes': fields.Integer,
        'is_liked': IsQuoteLikedByCurrentUser(attribute='id'),
        'created_at': fields.DateTime(dt_format='iso8601'),
        'updated_at': fields.DateTime(dt_format='iso8601'),
    }
}

quotes_fields = {
    'curr_page': fields.Integer(attribute='page'),
    'next_page': PaginationUrl(attribute='next_num'),
    'prev_page': PaginationUrl(attribute='prev_num'),
    'per_page': fields.Integer(attribute='per_page'),
    'total': fields.Integer(attribute='total'),
    'data': fields.List(fields.Nested(quote_fields), attribute='items'),
}
